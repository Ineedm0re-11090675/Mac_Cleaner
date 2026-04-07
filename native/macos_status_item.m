#import <Cocoa/Cocoa.h>

static void (*g_open_main_callback)(void) = NULL;
static void (*g_open_dashboard_callback)(void) = NULL;
static void (*g_quick_cache_callback)(void) = NULL;
static void (*g_quick_memory_callback)(void) = NULL;
static void (*g_hide_callback)(void) = NULL;
static void (*g_quit_callback)(void) = NULL;

static NSStatusItem *g_status_item = nil;
static id g_status_target = nil;

static void mcc_append_native_status_log(NSString *message) {
    @autoreleasepool {
        NSString *path = @"/tmp/macos_cleaner_native_status.log";
        NSString *timestamp = [[NSDate date] description];
        NSString *line = [NSString stringWithFormat:@"[%@] %@\n", timestamp, message];
        NSFileManager *file_manager = [NSFileManager defaultManager];
        if (![file_manager fileExistsAtPath:path]) {
            [line writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
            return;
        }
        NSFileHandle *handle = [NSFileHandle fileHandleForWritingAtPath:path];
        if (handle == nil) {
            return;
        }
        @try {
            [handle seekToEndOfFile];
            [handle writeData:[line dataUsingEncoding:NSUTF8StringEncoding]];
        } @catch (__unused NSException *exception) {
        } @finally {
            [handle closeFile];
        }
    }
}

@interface MCCStatusItemTarget : NSObject
- (void)openMain:(id)sender;
- (void)openDashboard:(id)sender;
- (void)quickCache:(id)sender;
- (void)quickMemory:(id)sender;
- (void)hideApp:(id)sender;
- (void)quitApp:(id)sender;
@end

@implementation MCCStatusItemTarget
- (void)openMain:(id)sender {
    if (g_open_main_callback != NULL) {
        g_open_main_callback();
    }
}

- (void)openDashboard:(id)sender {
    if (g_open_dashboard_callback != NULL) {
        g_open_dashboard_callback();
    }
}

- (void)quickCache:(id)sender {
    if (g_quick_cache_callback != NULL) {
        g_quick_cache_callback();
    }
}

- (void)quickMemory:(id)sender {
    if (g_quick_memory_callback != NULL) {
        g_quick_memory_callback();
    }
}

- (void)hideApp:(id)sender {
    if (g_hide_callback != NULL) {
        g_hide_callback();
    }
}

- (void)quitApp:(id)sender {
    if (g_quit_callback != NULL) {
        g_quit_callback();
    }
}
@end

static NSImage *mcc_make_status_icon(void) {
    const CGFloat canvas = 18.0;
    const CGFloat inset = 1.0;
    const CGFloat radius = 5.0;
    NSImage *image = [[NSImage alloc] initWithSize:NSMakeSize(canvas, canvas)];
    [image lockFocus];

    [[NSColor clearColor] setFill];
    NSRectFill(NSMakeRect(0, 0, canvas, canvas));

    NSBezierPath *rounded = [NSBezierPath bezierPathWithRoundedRect:NSMakeRect(inset, inset, canvas - inset * 2.0, canvas - inset * 2.0) xRadius:radius yRadius:radius];
    [[NSColor colorWithCalibratedWhite:1.0 alpha:0.98] setFill];
    [rounded fill];
    [[NSColor colorWithCalibratedWhite:0.05 alpha:0.18] setStroke];
    [rounded setLineWidth:1.0];
    [rounded stroke];

    NSDictionary *attributes = @{
        NSFontAttributeName: [NSFont boldSystemFontOfSize:8.5],
        NSForegroundColorAttributeName: [NSColor colorWithCalibratedWhite:0.06 alpha:1.0],
    };
    NSString *label = @"MC";
    NSSize text_size = [label sizeWithAttributes:attributes];
    NSRect text_rect = NSMakeRect(
        floor((canvas - text_size.width) / 2.0),
        floor((canvas - text_size.height) / 2.0) - 0.5,
        text_size.width,
        text_size.height
    );
    [label drawInRect:text_rect withAttributes:attributes];

    [image unlockFocus];
    return image;
}

bool mcc_install_status_item(
    void (*open_main_callback)(void),
    void (*open_dashboard_callback)(void),
    void (*quick_cache_callback)(void),
    void (*quick_memory_callback)(void),
    void (*hide_callback)(void),
    void (*quit_callback)(void)
) {
    mcc_append_native_status_log(@"mcc_install_status_item called");
    g_open_main_callback = open_main_callback;
    g_open_dashboard_callback = open_dashboard_callback;
    g_quick_cache_callback = quick_cache_callback;
    g_quick_memory_callback = quick_memory_callback;
    g_hide_callback = hide_callback;
    g_quit_callback = quit_callback;

    if (g_status_item != nil) {
        mcc_append_native_status_log(@"status item already exists");
        return true;
    }

    g_status_target = [[MCCStatusItemTarget alloc] init];
    if (g_status_target == nil) {
        mcc_append_native_status_log(@"failed: target allocation returned nil");
        return false;
    }

    NSStatusBar *status_bar = [NSStatusBar systemStatusBar];
    g_status_item = [status_bar statusItemWithLength:NSSquareStatusItemLength];
    if (g_status_item == nil) {
        mcc_append_native_status_log(@"failed: statusItemWithLength returned nil");
        g_status_target = nil;
        return false;
    }

    NSStatusBarButton *button = [g_status_item button];
    if (button != nil) {
        [button setTitle:@""];
        [button setToolTip:@"macOS Cleaner"];
        [button setImage:mcc_make_status_icon()];
        [button setImagePosition:NSImageOnly];
        mcc_append_native_status_log(@"button created and custom MC status icon set");
    } else {
        mcc_append_native_status_log(@"warning: status item button is nil");
    }

    NSMenu *menu = [[NSMenu alloc] initWithTitle:@"macOS Cleaner"];
    if (menu == nil) {
        mcc_append_native_status_log(@"failed: menu allocation returned nil");
        [status_bar removeStatusItem:g_status_item];
        g_status_item = nil;
        g_status_target = nil;
        return false;
    }

    NSMenuItem *open_main_item = [[NSMenuItem alloc] initWithTitle:@"打开主窗口" action:@selector(openMain:) keyEquivalent:@""];
    [open_main_item setTarget:g_status_target];
    [menu addItem:open_main_item];

    NSMenuItem *open_dashboard_item = [[NSMenuItem alloc] initWithTitle:@"打开仪表盘" action:@selector(openDashboard:) keyEquivalent:@""];
    [open_dashboard_item setTarget:g_status_target];
    [menu addItem:open_dashboard_item];

    [menu addItem:[NSMenuItem separatorItem]];

    NSMenuItem *quick_cache_item = [[NSMenuItem alloc] initWithTitle:@"一键清理缓存" action:@selector(quickCache:) keyEquivalent:@""];
    [quick_cache_item setTarget:g_status_target];
    [menu addItem:quick_cache_item];

    NSMenuItem *quick_memory_item = [[NSMenuItem alloc] initWithTitle:@"一键释放可回收内存" action:@selector(quickMemory:) keyEquivalent:@""];
    [quick_memory_item setTarget:g_status_target];
    [menu addItem:quick_memory_item];

    [menu addItem:[NSMenuItem separatorItem]];

    NSMenuItem *hide_item = [[NSMenuItem alloc] initWithTitle:@"隐藏窗口" action:@selector(hideApp:) keyEquivalent:@""];
    [hide_item setTarget:g_status_target];
    [menu addItem:hide_item];

    [menu addItem:[NSMenuItem separatorItem]];

    NSMenuItem *quit_item = [[NSMenuItem alloc] initWithTitle:@"退出" action:@selector(quitApp:) keyEquivalent:@""];
    [quit_item setTarget:g_status_target];
    [menu addItem:quit_item];

    [g_status_item setMenu:menu];
    mcc_append_native_status_log(@"status item installed successfully");
    return true;
}

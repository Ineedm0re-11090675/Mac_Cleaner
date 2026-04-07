#import <Cocoa/Cocoa.h>
#import <objc/runtime.h>

static void (*g_reopen_callback)(void) = NULL;
static IMP g_original_reopen_imp = NULL;
static BOOL g_installed = NO;

static BOOL macos_cleaner_should_handle_reopen(id self, SEL _cmd, NSApplication *app, BOOL hasVisibleWindows) {
    if (g_reopen_callback != NULL) {
        g_reopen_callback();
    }
    if (g_original_reopen_imp != NULL && g_original_reopen_imp != (IMP)macos_cleaner_should_handle_reopen) {
        BOOL (*original_fn)(id, SEL, NSApplication *, BOOL) = (BOOL (*)(id, SEL, NSApplication *, BOOL))g_original_reopen_imp;
        return original_fn(self, _cmd, app, hasVisibleWindows);
    }
    return YES;
}

void mcc_install_reopen_handler(void (*callback)(void)) {
    g_reopen_callback = callback;
    if (g_installed) {
        return;
    }

    NSApplication *app = [NSApplication sharedApplication];
    id delegate = [app delegate];
    if (delegate == nil) {
        return;
    }

    Class delegate_class = [delegate class];
    SEL selector = @selector(applicationShouldHandleReopen:hasVisibleWindows:);
    Method method = class_getInstanceMethod(delegate_class, selector);

    if (method != NULL) {
        g_original_reopen_imp = method_getImplementation(method);
        method_setImplementation(method, (IMP)macos_cleaner_should_handle_reopen);
    } else {
        class_addMethod(delegate_class, selector, (IMP)macos_cleaner_should_handle_reopen, "c@:@c");
    }

    g_installed = YES;
}

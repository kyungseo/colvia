// The OS supplies only a random event ID. The managed reader supplies all displayed text.
#import <AppKit/AppKit.h>
#import <CoreServices/CoreServices.h>
#import <UserNotifications/UserNotifications.h>
#import <poll.h>
#import <unistd.h>

static NSString *const missing = @"이 알림의 기록을 열 수 없습니다. 프로젝트 채팅에서 맡긴 작업의 질문이나 결과를 확인해 주세요.";

static BOOL validID(NSString *value) {
    return [value isKindOfClass:NSString.class] && value.length == 32 &&
        [value rangeOfCharacterFromSet:[[NSCharacterSet characterSetWithCharactersInString:@"0123456789abcdef"] invertedSet]].location == NSNotFound;
}

static NSString *readDetail(NSString *event) {
    if (!validID(event)) return missing;
    NSURL *bin = NSBundle.mainBundle.bundleURL.URLByDeletingLastPathComponent;
    NSTask *reader = [NSTask new];
    reader.executableURL = [bin URLByAppendingPathComponent:@"colvia-manage"];
    reader.arguments = @[@"notice-detail", @"--event", event];
    NSPipe *pipe = [NSPipe pipe];
    reader.standardOutput = pipe;
    reader.standardInput = NSFileHandle.fileHandleWithNullDevice;
    reader.standardError = NSFileHandle.fileHandleWithNullDevice;
    if (![reader launchAndReturnError:nil]) return missing;
    NSMutableData *data = [NSMutableData data];
    int fd = pipe.fileHandleForReading.fileDescriptor;
    NSTimeInterval end = NSProcessInfo.processInfo.systemUptime + 25;
    BOOL complete = NO;
    while (data.length <= 131072) {
        int ms = (int)((end - NSProcessInfo.processInfo.systemUptime) * 1000);
        struct pollfd item = {fd, POLLIN, 0};
        if (ms <= 0 || poll(&item, 1, ms) <= 0) break;
        char bytes[8192];
        ssize_t count = read(fd, bytes, sizeof(bytes));
        if (count <= 0) { complete = count == 0; break; }
        [data appendBytes:bytes length:(NSUInteger)count];
    }
    if (!complete) { if (reader.running) [reader terminate]; return missing; }
    [reader waitUntilExit];
    NSString *text = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    return reader.terminationStatus == 0 && text.length ? text : missing;
}

@interface WorkWindow : NSObject <NSApplicationDelegate, UNUserNotificationCenterDelegate>
@property(strong) NSWindow *window;
@property(strong) NSTextView *text;
@property NSUInteger sequence;
@end

@implementation WorkWindow
- (void)applicationWillFinishLaunching:(NSNotification *)note {
    [UNUserNotificationCenter currentNotificationCenter].delegate = self;
}
- (void)show:(NSString *)event {
    const NSUInteger generation = ++self.sequence;
    if (!self.window) {
        self.window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,540,340)
            styleMask:NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable
            backing:NSBackingStoreBuffered defer:NO];
        self.window.title = @"Colvia · 맡긴 작업"; self.window.releasedWhenClosed = NO;
        NSScrollView *scroll = [NSTextView scrollableTextView];
        self.text = (NSTextView *)scroll.documentView;
        self.text.editable = NO; self.text.richText = NO; self.text.automaticLinkDetectionEnabled = NO;
        self.text.textContainerInset = NSMakeSize(18,18);
        self.text.font = [NSFont systemFontOfSize:15];
        self.window.contentView = scroll;
        [self.window center];
    }
    self.text.string = @"작업 기록을 확인하고 있습니다.";
    [self.window makeKeyAndOrderFront:nil]; [NSApp activateIgnoringOtherApps:YES];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0), ^{
        NSString *value = readDetail(event);
        dispatch_async(dispatch_get_main_queue(), ^{
            if (generation == self.sequence) { self.text.string = value; [self.text scrollRangeToVisible:NSMakeRange(0,0)]; }
        });
    });
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender { return YES; }
- (void)userNotificationCenter:(UNUserNotificationCenter *)center didReceiveNotificationResponse:(UNNotificationResponse *)r
         withCompletionHandler:(void (^)(void))done {
    if (![r.actionIdentifier isEqualToString:@"view"] && ![r.actionIdentifier isEqualToString:UNNotificationDefaultActionIdentifier]) {
        done(); return;
    }
    NSString *event = r.notification.request.content.userInfo[@"id"];
    if (!validID(event) || ![event isEqualToString:r.notification.request.identifier]) event = nil;
    dispatch_async(dispatch_get_main_queue(), ^{ [self show:event]; done(); });
}
@end

static int post(NSString *event) {
    if (event && !validID(event)) return 1;
    [NSApplication sharedApplication];
    if (LSRegisterURL((__bridge CFURLRef)NSBundle.mainBundle.bundleURL, true) != noErr) return 1;
    UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
    UNNotificationAction *action = [UNNotificationAction actionWithIdentifier:@"view" title:@"보기" options:UNNotificationActionOptionForeground];
    [center setNotificationCategories:[NSSet setWithObject:[UNNotificationCategory categoryWithIdentifier:@"work"
        actions:@[action] intentIdentifiers:@[] options:UNNotificationCategoryOptionNone]]];
    __block int result = -1;
    [center requestAuthorizationWithOptions:UNAuthorizationOptionAlert completionHandler:^(BOOL granted,NSError *error) {
        if (!granted || error) { dispatch_async(dispatch_get_main_queue(), ^{ result=1; }); return; }
        if (!event) { dispatch_async(dispatch_get_main_queue(), ^{ result=0; }); return; }
        UNMutableNotificationContent *content = [UNMutableNotificationContent new];
        content.title = @"Colvia · 맡긴 작업"; content.body = @"새 소식이 있습니다. 눌러서 작업을 확인하세요.";
        content.categoryIdentifier = @"work"; content.userInfo = @{@"id":event};
        UNNotificationRequest *request = [UNNotificationRequest requestWithIdentifier:event content:content
            trigger:[UNTimeIntervalNotificationTrigger triggerWithTimeInterval:2 repeats:NO]];
        [center addNotificationRequest:request withCompletionHandler:^(NSError *err) {
            dispatch_async(dispatch_get_main_queue(), ^{ result=err ? 1 : 0; });
        }];
    }];
    NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:25];
    while (result < 0 && deadline.timeIntervalSinceNow > 0)
        [[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.1]];
    return result == 0 ? 0 : 1;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc == 2 && strcmp(argv[1],"--authorize") == 0) return post(nil);
        if (argc == 3 && strcmp(argv[1],"--post") == 0)
            return post([NSString stringWithUTF8String:argv[2]]);
        NSApplication *app = NSApplication.sharedApplication;
        WorkWindow * __attribute__((objc_precise_lifetime)) delegate = [WorkWindow new];
        app.delegate = delegate;
        [app setActivationPolicy:NSApplicationActivationPolicyRegular]; [app run];
    }
    return 0;
}

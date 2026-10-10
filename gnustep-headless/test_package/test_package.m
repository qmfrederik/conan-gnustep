#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>

int main(void)
{
    NSAutoreleasePool *pool = [NSAutoreleasePool new];

    // Initializing NSApplication loads the headless backend bundle and server.
    NSApplication *app = [NSApplication sharedApplication];
    if (app == nil)
    {
        NSLog(@"Failed to create NSApplication");
        return 1;
    }

    // Creating a window requires a working (headless) backend.
    NSWindow *window = [[NSWindow alloc] initWithContentRect: NSMakeRect(0, 0, 100, 100)
                                                   styleMask: NSTitledWindowMask
                                                     backing: NSBackingStoreBuffered
                                                       defer: NO];
    if (window == nil)
    {
        NSLog(@"Failed to create an NSWindow");
        return 1;
    }

    NSLog(@"Created a window using %@", NSStringFromClass([[NSGraphicsContext currentContext] class]));

    [window release];
    [pool release];
    return 0;
}

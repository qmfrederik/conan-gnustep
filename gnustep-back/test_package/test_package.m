#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>

int main(int argc, const char *argv[])
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
    NSWindow *window = [[NSWindow alloc] initWithContentRect: NSMakeRect(0, 0, 300, 100)
                                                   styleMask: NSTitledWindowMask
                                                     backing: NSBackingStoreBuffered
                                                       defer: NO];
    if (window == nil)
    {
        NSLog(@"Failed to create an NSWindow");
        return 1;
    }

    NSLog(@"Created a window using %@", NSStringFromClass([[NSGraphicsContext currentContext] class]));

    [window setTitle: @"test_package"];

    NSTextField *label = [[NSTextField alloc] initWithFrame: NSMakeRect(20, 35, 260, 30)];
    [label setStringValue: @"Hello from gnustep-back"];
    [label setEditable: NO];
    [label setBezeled: NO];
    [label setDrawsBackground: NO];
    [[window contentView] addSubview: label];
    [label release];

    [window makeKeyAndOrderFront: nil];

    // Render the window's content view into a bitmap and write it out as a TIFF.
    NSView *view = [window contentView];
    NSBitmapImageRep *rep = [view bitmapImageRepForCachingDisplayInRect: [view bounds]];
    [view cacheDisplayInRect: [view bounds] toBitmapImageRep: rep];

    NSData *tiff = [rep representationUsingType: NSTIFFFileType properties: nil];
    if (tiff == nil)
    {
        NSLog(@"Failed to encode the screenshot as TIFF");
        return 1;
    }

    NSString *path = argc > 1 ? [NSString stringWithUTF8String: argv[1]] : @"screenshot.tiff";
    if (![tiff writeToFile: path atomically: YES])
    {
        NSLog(@"Failed to save screenshot to %@", path);
        return 1;
    }

    NSLog(@"Saved screenshot to %@", [path stringByStandardizingPath]);

    [window release];
    [pool release];
    return 0;
}

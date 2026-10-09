#import <Foundation/Foundation.h>
#import <AppKit/NSColor.h>

int main(void)
{
    NSAutoreleasePool *pool = [NSAutoreleasePool new];

    // NSColor doesn't need a display server or a backend.
    NSColor *color = [NSColor redColor];
    if (color == nil)
    {
        NSLog(@"Failed to create an NSColor");
        return 1;
    }

    NSLog(@"Created an instance of %@", NSStringFromClass([color class]));

    [pool release];
    return 0;
}

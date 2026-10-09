#import <Foundation/Foundation.h>
#import <PreferencePanes/PreferencePanes.h>

int main(void)
{
    NSAutoreleasePool *pool = [NSAutoreleasePool new];

    NSPreferencePane *pane = [[NSPreferencePane alloc] init];
    if (pane == nil)
    {
        NSLog(@"Failed to create an NSPreferencePane");
        return 1;
    }

    NSLog(@"Created an instance of %@", NSStringFromClass([pane class]));
    [pane release];

    [pool release];
    return 0;
}

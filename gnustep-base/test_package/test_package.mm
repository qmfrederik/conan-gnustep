#include <assert.h>

#import <Foundation/Foundation.h>

@interface Test : NSObject
@end

@implementation Test
+ throwException
{
    [NSException raise: NSGenericException format: @"Exception from test class"];
}
@end

int main(void)
{
    // Compiling this file requires -fobjc-exceptions (and -fblocks, where supported; GCC has no blocks) to be applied to Objective C++ sources.
    int exceptionThrown = 0;
    @try
    {
        [Test throwException];
    }
    @catch (id e)
    {
        exceptionThrown = 1;
    }

    assert(exceptionThrown);

#ifdef __BLOCKS__
    __block int blockCalled = 0;
    void (^block)(void) = ^{ blockCalled = 1; };
    block();
    assert(blockCalled);
#endif

    NSLog(@"[PASS]: Objective C++ compiler flags");
    return 0;
}

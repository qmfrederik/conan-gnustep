#include <stdlib.h>
#include <assert.h>

#import <Foundation/NSException.h>

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
    // This ensures we have a healty Objective C development environment once gnustep-make has been configured.
    // In particular, we're testing the various Objective C compiler options (ABI, exception model,...) are configured
    // correctly, by invoking an Objective C method which throws.
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

    return EXIT_SUCCESS;
}
#include <stdlib.h>
#include <assert.h>

#ifdef __has_attribute
#if __has_attribute(objc_root_class)
__attribute__((objc_root_class))
#endif
#endif
@interface Test
{
    id isa; 
}
@end

@implementation Test
+ throwException
{
    @throw self;
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
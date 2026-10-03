#include <stdlib.h>
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
    // Basic tests of gnustep-base
    NSLog(@"Hello, World!");

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

    // gnustep-base uses ICU for locale and date support; this crashes (SIGSEGV in udat_setLenient) when the ICU data is not available at runtime.
    NSAutoreleasePool *pool = [NSAutoreleasePool new];
    NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
    [formatter setLocale:[NSLocale localeWithLocaleIdentifier:@"en_US"]];
    [formatter setTimeZone:[NSTimeZone timeZoneWithName:@"UTC"]];
    [formatter setDateFormat:@"EEEE, MMMM d, yyyy"];
    [formatter setLenient:YES];
    NSString *formatted = [formatter stringFromDate:[NSDate dateWithTimeIntervalSince1970:0]];
    NSLog(@"Formatted date: %@", formatted);
    int dateFormatOk = [formatted isEqualToString:@"Thursday, January 1, 1970"];
    [formatter release];
    [pool release];

    if (!dateFormatOk)
        return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
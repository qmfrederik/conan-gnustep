#include <stdlib.h>
#include <assert.h>
#ifndef _WIN32
#include <unistd.h>
#endif

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
#ifndef _WIN32
    // Further down in this test, we will make sure that GNUstep-base can read time-zone data from the timezone package embedded
    // in the GNUstep-base bundle itself.  To make sure GNUstep-base wouldn't accidentally pick pu time zone data which is installed
    // by the operating system, set TZDIR to an empty directory.
    char emptyZoneDir[] = "/tmp/test_package_zoneinfo_XXXXXX";
    assert(mkdtemp(emptyZoneDir) != NULL);
    setenv("TZDIR", emptyZoneDir, 1);
#endif

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
    // We work around this by embedding the ICU data within the GNUstep-base library itself.
    NSAutoreleasePool *pool = [NSAutoreleasePool new];
    NSDateFormatter *formatter = [[NSDateFormatter alloc] init];
    [formatter setLocale:[NSLocale localeWithLocaleIdentifier:@"en_US"]];
    [formatter setTimeZone:[NSTimeZone timeZoneWithName:@"UTC"]];
    [formatter setDateFormat:@"EEEE, MMMM d, yyyy"];
    [formatter setLenient:YES];
    NSString *formatted = [formatter stringFromDate:[NSDate dateWithTimeIntervalSince1970:0]];
    int dateFormatOk = [formatted isEqualToString:@"Thursday, January 1, 1970"];
    NSLog(@"[%@]: Date format %@", dateFormatOk ? @"PASS" : @"FAIL", formatted);
    [formatter release];

    // The gnustep-base resource bundle (NSTimeZones, ...) must be found at runtime. If the library domain is not
    // configured, bundleForClass: falls back to the main bundle and this lookup fails.  The default GNUstep.conf
    // doesn't work because conan packages can be installed anywhere on the file system, and GNUstep.conf contains
    // hard-coded paths.
    NSBundle *baseBundle = [NSBundle bundleForClass:[NSObject class]];
    NSString *regionsPath = [baseBundle pathForResource:@"regions" ofType:nil inDirectory:@"NSTimeZones"];
    int bundleOk = (regionsPath != nil);
    NSLog(@"[%@]: Bundle path %@ for bundle %@", bundleOk ? @"PASS" : @"FAIL", regionsPath ? regionsPath : @"nil", baseBundle);

    // Without the bundle and without system zoneinfo this raises NSInvalidArgumentException
    // (nil path passed to -[NSFileManager enumeratorAtPath:]) from +[NSTimeZone timeZoneArray].
    int abbreviationOk = 0;
    @try
    {
        NSTimeZone *zone = [NSTimeZone timeZoneWithAbbreviation:@"PST"];
        NSLog(@"PST time zone: %@", zone);
        abbreviationOk = (zone != nil);
    }
    @catch (NSException *e)
    {
        NSLog(@"timeZoneWithAbbreviation: raised %@: %@", [e name], [e reason]);
    }

    NSLog(@"[%@]: Time zone abbreviation lookup", abbreviationOk ? @"PASS" : @"FAIL");

    [pool release];

    if (!dateFormatOk || !bundleOk || !abbreviationOk)
        return EXIT_FAILURE;

    return EXIT_SUCCESS;
}
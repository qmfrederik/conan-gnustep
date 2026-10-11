#import <Foundation/Foundation.h>
#import <AppKit/NSColor.h>
#import <AppKit/NSBitmapImageRep.h>
#import <AppKit/NSGraphics.h>

#define SIZE 64

static NSBitmapImageRep *MakeBitmap(BOOL hasAlpha)
{
    NSBitmapImageRep *rep = [[[NSBitmapImageRep alloc]
        initWithBitmapDataPlanes:NULL
                      pixelsWide:SIZE
                      pixelsHigh:SIZE
                   bitsPerSample:8
                 samplesPerPixel:hasAlpha ? 4 : 3
                        hasAlpha:hasAlpha
                        isPlanar:NO
                  colorSpaceName:NSDeviceRGBColorSpace
                     bytesPerRow:0
                    bitsPerPixel:0] autorelease];
    if (rep == nil)
    {
        return nil;
    }

    // libs-gui's JPEG writer overflows its buffer when the output exceeds the raw size (headers
    // alone are ~700 bytes), so the bitmap must be large and smooth enough to compress well.
    unsigned char *pixels = [rep bitmapData];
    NSUInteger length = [rep bytesPerRow] * [rep pixelsHigh];
    NSUInteger i;
    for (i = 0; i < length; i++)
    {
        pixels[i] = (unsigned char)(i / 64);
    }
    return rep;
}

// Decodes data through the codec library and checks the resulting dimensions.
static BOOL CheckDecode(NSData *data, NSString *format, NSInteger width, NSInteger height)
{
    NSBitmapImageRep *decoded = [[[NSBitmapImageRep alloc] initWithData:data] autorelease];
    if (decoded == nil)
    {
        NSLog(@"Failed to decode the %@ image (%lu bytes): initWithData: returned nil",
              format, (unsigned long)[data length]);
        return NO;
    }
    if ([decoded pixelsWide] != width || [decoded pixelsHigh] != height)
    {
        NSLog(@"Failed to decode the %@ image: expected %ldx%ld but got %ldx%ld",
              format, (long)width, (long)height,
              (long)[decoded pixelsWide], (long)[decoded pixelsHigh]);
        return NO;
    }

    NSLog(@"Decoded a %ldx%ld %@ image", (long)[decoded pixelsWide], (long)[decoded pixelsHigh], format);
    return YES;
}

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

    NSBitmapImageRep *rgba = MakeBitmap(YES);
    NSBitmapImageRep *rgb = MakeBitmap(NO);
    if (rgba == nil || rgb == nil)
    {
        NSLog(@"Failed to create an NSBitmapImageRep");
        return 1;
    }

    // PNG: round-trip through the libpng encoder and decoder.
    NSData *png = [rgba representationUsingType:NSPNGFileType properties:nil];
    if ([png length] < 8 || memcmp([png bytes], "\x89PNG\r\n\x1a\n", 8) != 0)
    {
        NSLog(@"Failed to encode the bitmap as PNG");
        return 1;
    }
    if (!CheckDecode(png, @"PNG", SIZE, SIZE))
    {
        return 1;
    }

    // TIFF: round-trip through libtiff.
    NSData *tiff = [rgba representationUsingType:NSTIFFFileType properties:nil];
    if ([tiff length] < 4
        || (memcmp([tiff bytes], "II*\0", 4) != 0 && memcmp([tiff bytes], "MM\0*", 4) != 0))
    {
        NSLog(@"Failed to encode the bitmap as TIFF");
        return 1;
    }
    if (!CheckDecode(tiff, @"TIFF", SIZE, SIZE))
    {
        return 1;
    }

    // JPEG: round-trip through libjpeg (JPEG has no alpha channel).
    NSData *jpeg = [rgb representationUsingType:NSJPEGFileType properties:nil];
    if ([jpeg length] < 3 || memcmp([jpeg bytes], "\xff\xd8\xff", 3) != 0)
    {
        NSLog(@"Failed to encode the bitmap as JPEG");
        return 1;
    }
    if (!CheckDecode(jpeg, @"JPEG", SIZE, SIZE))
    {
        return 1;
    }

    // GIF: decode a fixed 1x1 image, since encoding depends on optional giflib quantization support.
    static const unsigned char gifBytes[] = {
        'G', 'I', 'F', '8', '9', 'a', 0x01, 0x00, 0x01, 0x00, 0x80, 0x00, 0x00,
        0x00, 0x00, 0x00, 0xff, 0xff, 0xff,
        0x21, 0xf9, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x2c, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
        0x02, 0x02, 0x44, 0x01, 0x00, 0x3b
    };
    NSData *gif = [NSData dataWithBytes:gifBytes length:sizeof(gifBytes)];
    if (!CheckDecode(gif, @"GIF", 1, 1))
    {
        return 1;
    }

    [pool release];
    return 0;
}

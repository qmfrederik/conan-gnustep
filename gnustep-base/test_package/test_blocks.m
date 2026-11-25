#import <Foundation/Foundation.h>

typedef int (^IntBlock)(void);

// Returns a block which outlives the stack frame that created it.
static IntBlock makeCounter(void)
{
    __block int count = 0;
    return Block_copy(^{ return ++count; });
}

// Tests the blocks syntax: block literals with parameters, captured variables and __block variables.
int testBlocks(void)
{
    int offset = 10;
    int (^add)(int) = ^(int x) { return x + offset; };
    int captureOk = (add(1) == 11);

    __block int total = 0;
    void (^accumulate)(int) = ^(int x) { total += x; };
    accumulate(2);
    accumulate(3);
    int blockVariableOk = (total == 5);

    IntBlock counter = makeCounter();
    int escapingOk = (counter() == 1) && (counter() == 2);
    Block_release(counter);

    return captureOk && blockVariableOk && escapingOk;
}

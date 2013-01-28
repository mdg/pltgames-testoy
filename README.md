
Testoy the PLT Games Programming Language
============

Testoy is a programming language created as an entry to the PLT Games

http://www.pltgames.com/competition/2013/1

It is not meant to be used, except as a demonstration of features that
might be added to other, more complete languages.

The code part of Testoy is fairly generic, functions are defined much as
in other languages.

```
func main()
    ## This is a comment
    x <- 5
    y <- x + 7
    print(y)
    return y
end
```


Novelty
=========

The parts of Testoy that are meant to be novel are its features for testing.
Testoy implements four special test-specific syntaxes to make tests easier
to read and write.
* Pure Function Tests
* Manual Test Sets
* Given Statements
* Test Functions
* Test Patches (not implemented)

Pure Function Tests
------

Testing pure functions is the simplest kind of test. A function takes in
some data and has output. Testoy has direct support for this.

Imagine that we want to test
a function that takes 2 parameters and simply divides one by the other.

```
func divide(top, bottom)
    return top / bottom
end
```

We know the basic inputs and outputs to test this function, and we just want
to tell Testoy what they are with the `puretest ... given` syntax.
Each line in the
pure test represents the inputs and output from the divide function.
When 8 and 2 are passed to divide, the result is 4. Likewise for the remaining
lines in the given data.

```
puretest divide given
	8 -> 2 -> 4
	-10 -> 5 -> 2
	21 -> -3 -> -7
	0 -> 2 -> 0
end
```

Manual Test Sets
------

Testoy provides syntactic sugar for definiting manual test data sets.

In this example, we want to test the thrice function.

```
func thrice(n)
    return n * 3
end
```

The testdata ... provide syntax defines a set of test data that can be
accessed by tests. This data is whitespace separated and divided by lines.

```
testdata thrice_testdata provide
     12  4
    -3 -1
     0  0
end
```

The given keyword takes a list of data and causes the test to be run once
for each item in the list.

```
test thrice_provided
	given expected, input <- thrice_testdata
	expected = thrice(input)
end
```

Test Functions
------

Consider again the `divide` function from above. We want to test it with
an inverse function to make sure it's working. However, we don't want that
inverse function showing up in the actual code.

The `testfunc` syntax will do this. It's exactly like regular function
definitions, but the `testfunc` will not be available except when running in
the test context.

```
testfunc multiply(a, b)
	return a * b
end
```

Given
------

The `given` keyword was already used when loading a test data set in the
example above. Tests can start off with any number of given statements
for setting test data. For the first given statement, a test case is
created for each row of data in the list. For subsquent given statements
every existing test case is duplicated for each case in the new given
statement, as in an outer join.

In this example, x and y are each assigned a list of 10 random integers. The
test will be executed once for each combination of x and y, resulting in
100 tests being run in total.

Within tests, assertion is implied, so they are made simply by stating
an expression that should be true. `a = b` will cause the test to fail
if a does not equal b.

```
## get a result and test that it is the inverse of of a test function
test multiply_inverse_divide
	given x <- generate(10, random_int)
	given y <- generate(10, random_int)

	## this line calls the multiply testfunc
	z <- multiply(x, y)

	## the next 2 lines are assertions
	## if they do not evaluate to true, the test will fail
	y = divide(z, x)
	x = divide(z, y)
end
```

Test Patches (not implemented)
-------------

Sometimes, in the course of testing, a function may be called expecting the
system to be in a particular state. Since it is in the test context, this
state may not be correctly initialized and executing the function will fail.
One solution for this is to use
[Mocks](http://en.wikipedia.org/wiki/Mock_object).

Testoy addresses this with the `patch` statement used for overriding
existing functions within tests.

```
test time_difference_function_test
	patch time() -> 1000
	patch time() -> 1005
	## subsequent calls to time() will return 1000 and then 1005
	##
	## the tested function should return the difference between 2 calls
	## to time. given the data above should be 5
	result <- time_difference_function()
	5 = result
end

test product_comparison
	x <- create_product(1001, "Brand X TV")
	y <- create_product(1002, "Brand Y TV")

	## patch can also be used in conjunction with parameters
	## calls to find_product_by_id for each ID will return the given value
	## Calls with other parameters will be unaffected
	patch find_product_by_id(1001) -> x
	patch find_product_by_id(1002) -> y

	## find_products_to_compare calls find_product_by_id
	result <- find_products_to_compare(1001, 1002)
	1001 = product_id(first_product(result))
	1002 = product_id(second_product(result))
end
```

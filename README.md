# FP test generator
Random floating-point testcase generator for SMT-LIB. This was
originally part of [PyMPF](https://github.com/florianschanda/PyMPF),
but it is actually cleaner to separate out the library part from the
test-case generator.

This program creates small benchmarks for SMT-LIB that involve the
[Floating Point](http://smtlib.cs.uiowa.edu/theories-FloatingPoint.shtml)
theory. The benchmarks created focus on checking for correct behaviour
as opposed to performance. This was part of the verification argument of our
[TACAS'2019](https://link.springer.com/chapter/10.1007/978-3-030-17462-0_5)
paper.

We used this to find soundness and completness bugs in *all* floating
point solvers we tried (that could understand SMT-LIB). For the FP
solvers that do not support SMT-LIB we're pretty sure we could also
find bugs but honestly we can't be bothered to support different
formats other than SMT-LIB.

To make sure the expected status (SAT/UNSAT) of each test is correct
we are independently checking against as many of the following as is
possible:

* PyMPF (this is the main test oracle and the only library that
  supports everything)

* MPFR (does not support RNA, except for roundToIntegral)

* Your FPU (probably only supports float32 and float64, and does not
  support RNA except for roundToIntegral)

Note that the tests generated may rely on unspecified behaviour
(following a strict reading of the FP theory): for example tests that
involve min/max for +0 and -0 may rely on min/max being returning
*either* of the two. Similarly for conversions to bitvectors that are
out of range.

## Dependencies
This project requires the following Python3 packages:
* [PyMPF](https://pypi.org/project/pympf) (the main test oracle)
* [gmpy2](https://pypi.org/project/gmpy2) (to interface with MPFR)

This project requires the following system dependencies:
* gcc (to build tiny C programs)

To install these on Debian based systems do as root:
```
$ apt-get install python3-pip libmpc-dev libmpfr-dev
```

And then:
```
$ pip3 install PyMPF gmpy2
```

## Work in progress
This is a complete re-write of the original tool in Python3. It does
not yet work completely. If you want the original tool, look at the
python2 branch of PyMPF.

# License and Copyright
Everything in this repository is licensed under the GNU GPL v3. The
sole copyright owner is Florian Schanda.

# Lawn

Interpreter, documentation and sample code for Lawn, an esoteric, minimalist, functional programming language, based on Grass.

## Running Lawn Programs

The interpreter is written for Python 3.

    $ python lawn.py <filename>

## Introduction

The esoteric functional programming language [Grass](http://www.blue.sky.or.jp/grass/) is absolutely fascinating, allowing for Turing-complete functional programing, with only three characters `w`, `W`, and `v`. However, in conjunction with being entirely stack-based, and forcing all its code to be lists of indices that change after each function application and definition, this makes Grass programs nearly unreadble and gives the language a huge learning curve.

Grass, nonetheless, in its simplicty, offers a good framework for a minimalist programming language to demonstrate the basics of Lambda calculus and functional programming. This project, **Lawn**, improves on it by allowing for the use of labels to refer to elements on the stack, using actual numbers to refer to stack indices, and generally making the structure of programs more clear.

The interpreter included here is a simply a modified [Grass interpreter](https://web.archive.org/web/20151029091504/http://coderepos.org:80/share/browser/lang/python/grass/grass.py) originally created by NISHIO Hirokazu, updated for Python 3, and with the initial parsing reconfigured to support the Lawn language standards described below.

I don't know much about coding, or functional programming, so I apologize if this is imprecisly done.

## Language Standards

### Syntax

A Lawn program consists of four components: function applications, function defintions, labeling commands, and comments. A program must begin with a function definition. Anything before the first function definition will be ignored.

#### Function Applications

A function aplication consists of two indexes, separated from the rest of the program and each other by whitespace. It calls the function of the first index to be applied to the function in the second index. Function and argument indices may be called by the following ways:

    '           Index 1 (top of stack)
    '<number>   Index <number>, where number is greater than 0.
    <label>     Index of item on stack asssigned to <label>, 
                including user-defined labels, 
                predefined primitive labels, 
                and predefined function argument labels.

An example function application looks like this:

    ' out   # apply function on top of stack to primitive function out #

#### Function Definitions

A function defintion takes the form

    <arity> <aplications and labeling commands> ]

where `<arity>` is a number greater than 0 representing the number of arguments the function takes. `<applications and labeling commands>` is a series of applications and labeling commands that the function will apply when called. Note that functions cannot be nested. A `]` closes the function definition. The interpreter treats `]` as ` ] `, so whitespace is optional around it.

When a function is defined, the interpreter automatically creates labels for each argument. These take the form `.<n>` where `<n>` is the number of the argument, in the order that they are passed to the function. So, a function with arity 4 would have argument labels `.1`, `.2`, `.3`, and `.4`.

An example function looks like this:

    2 .1 .2 ]   # Church integer 1: \fa.f a #

#### Labeling Commands

A labeling command takes the form

    : <label>
    
where label is a sting of characters. The interpreter treats `:` as ` : `, so whitespace is optional around it.
A label may not contain `:` or `]`, nor may it be of the form `'` or `'<number ≥ 1>` or `.<number ≥ 1>`, to avoid collisions with other index referents.
A label is unique, so a newly defined label may not be the same as an old one. Labels defined inside a function are local, and cannot be called outside of the function, and they must not collide with any any global labels created *before* the function definition.

When a labeling command is processed, it attaches the label to the function on the top of the stack. It does not add anything to the top of the stack.

An example labeling command looks like this:

    2 .1 .2 ]:one   # attach label 'one' to function #

#### Comments

Anything between two `#`s is ignored by the interpreter.

Example comment:

    # I feel powerless #


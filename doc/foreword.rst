Foreword
========

Read this before you get started with Pythonect. This hopefully answers some
questions about the purpose and goals of the project, and when you should or
should not be using it.

What is Pythonect?
------------------

Pythonect is a new, experimental, general-purpose dataflow programming
language based on Python. It provides both a visual programming language and a
text-based scripting language. The text-based scripting language aims to
combine the quick and intuitive feel of shell scripting, with the power of
Python. The visual programming language is based on the idea of a diagram with
"boxes and arrows".

The Pythonect interpreter (and reference implementation) is a free and open
source software written completely in Python, and is available under the BSD
license.

Why Pythonect?
--------------

Pythonect, being a dataflow programming language, treats data as something
that originates from a source, flows through a number of processing
components, and arrives at some final destination. As such, it is most
suitable for creating applications that are themselves focused on the "flow"
of data. Perhaps the most readily available example of a dataflow-oriented
applications comes from the realm of real-time signal processing, e.g. a video
signal processor which perhaps starts with a video input, modifies it through
a number of processing components (video filters), and finally outputs it to a
video display.

As with video, other domain problems (e.g. image processing, data analysis,
rapid prototyping, and etc.) can be expressed as a network of different
components that are connected by a number of communication channels. The
benefits, and perhaps the greatest incentives, of expressing a domain problem
this way is scalability and parallelism. The different components in the
network can be maneuvered to create entirely unique dataflows without
necessarily requiring the relationship to be hardcoded. Also, the design and
concept of components make it easier to run on distributed systems and
parallel processors.

Continue to :ref:`installation` or :ref:`tutorial`

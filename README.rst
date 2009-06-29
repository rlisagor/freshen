Freshen
=======

- Freshen is an acceptance testing framework for Python
- It is built as a plugin for Nose_
- It uses the (mostly) same syntax as Cucumber_

Most of the information shown here can also be found on the Cucumber wiki, but here it is anyway:

Freshen tests are composed of two parts: `feature outlines`_ and `step definitions`_.


Feature outlines
----------------

Feature outlines are text files with a ``.feature`` extension. The purpose of this file is to
describe a feature in plain text understandable by a non-technical person such as a product manager
or user. However, these files are specially formatted and are parsed by Freshen in order to execute
real tests.

You can put your feature files anywhere you want in the source tree of your project, but it is
recommended to place them in a dedicated "features" directory.

A feature file contains the feature name with a free-form text description, followed by one or more
`scenarios`_ or `scenario outlines`_.


Scenarios
---------

A scenario is an example of an interaction a user would have as part of the feature. It is comprised
of a series of *steps*. Each step has to start with a keyword: "Given", "When", "And", or "Then".
Here's an example for a calculator application (this example is included in the `source code`_)::

    Scenario: Divide regular numbers
      Given I have entered 3 into the calculator
      And I have entered 2 into the calculator
      When I press divide
      Then the result should be 1.5 on the screen


Scenario Outlines
-----------------

Sometimes it is useful to parametrize a scenario and run it multiple times, subsituting values. For
this purpose, use *scenario outlines*. The format is the same as a scenario, except you can indicate
places where a value should be subsituted using angle brackets: < and >. You specify the values
to be substituted using an "Examples" section that follows the scenario outline::

    Scenario Outline: Add two numbers
      Given I have entered <input_1> into the calculator
      And I have entered <input_2> into the calculator
      When I press <button>
      Then the result should be <output> on the screen

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |

In this case, the scenario will be executed once for each row in the table (except the first row,
which indicates which variable to subsitute for).


Step Definitions
----------------

When presented with a feature file, Freshen will execute each scenario which involves iterating over
each step in turn an executing its *step definition*. Step definitions are python functions adorned
with a special decorator. Freshen knows which step definition function to execute by matching the
step's text against a regular expression associated with the definition. Here's an example of a step
definition file, which hopefully illustrates this point::

    from freshen import *
    from freshen.checks import *

    import calculator
    
    @Before
    def before(sc):
        scc.calc = calculator.Calculator()
        scc.result = None
    
    @Given("I have entered (\d+) into the calculator")
    def enter(num):
        scc.calc.push(int(num))

    @When("I press (\w+)")
    def press(button):
        op = getattr(scc.calc, button)
        scc.result = op()

    @Then("the result should be (.*) on the screen")
    def check_result(value):
        assert_equal(str(scc.result), value)

In this example, you see a few step definitions, as well as a hook. Any captures (bits inside the 
parentheses) from the regular expression are passed to the step definition function as arguments.

Freshen will look for step definition modules in every directory where it finds ``.feature`` files.
The module should be named ``steps``. It can also be a python package, as long as all the
relevant functions are imported into ``steps/__init__.py``.


Hooks
-----

It is often useful to do some work before each step or each scenario is executed. For this purpose,
you can make use of *hooks*. Identify them for Freshen by adorning them with "@Before", "@After"
(run before or after each scenario), or "@AfterStep" which is run after each step.


Context storage
---------------

Since the execution each scenario is broken up between multiple step functions, it is often
necessary to share information between steps. It is possible to do this using global variables in
the step definition modules but, if you dislike that approach, Freshen provides three global
storage areas which can be imported from the `freshen` module. They are:

- ``glc``: Global context, never cleared - same as using a global variable
- ``ftc``: Feature context, cleared at the start of each feature
- ``scc``: Scenario context, cleared at the start of each scenario

These objects are built to mimic a JavaScript/Lua-like table, where fields can be accessed with
either the square bracket notation, or the attribute notation. The they do not complain when a key
is missing::

    gcc.stuff == gcc['stuff']  => True
    gcc.doesnotexist           => None


Multi-line arguments
--------------------

Steps can have two types of multi-line arguments: multi-line strings and tables. Multi-line strings
look like Python docstrings, starting and terminating with three double quotes: ``"""``.

Tables look like the ones in the example section in scenario outlines. They are comprised of a
header and one or more rows. Fields are delimited using a pipe: ``|``.

Both tables and multi-line strings should be placed on the line following the step.

They will be passed to the step definition as the first argument. Strings are presented as regular
Python strings, whereas tables come across as a ``Table`` object. To get the rows, call
``table.iterrows()``.


Tags
----

A feature or scenario can be adorned with one or more tags. This helps classify features and
scenarios to the reader. Freshen makes use of tags in two ways. The first is by allowing selective
execution via the command line - this is described below. The second is by allowing `hooks`_ to be
executed selectively. A partial example::
    
    >> feature:
    
    @needs_tmp_file
    Scenario: A scenario that needs a temporary file
        Given ...
        When ...
    
    >> step definition:
    
    @Before("@needs_tmp_file")
    def needs_tmp_file(sc):
        make_tmp_file()


Running
-------

Freshen runs as part of the nose framework, so all options are part of the ``nosetests`` command-
line tool.

Some useful flags for ``nosetests``:

- ``--with-freshen``: Enables Freshen
- ``-v``: Verbose mode will display each feature and scenario name as they are executed
- ``--tags``: Only run the features and scenarios with the given tags. Tags should follow this
  option as a comma-separated list. A tag may be prefixed with a tilde (``~``) to negate it and only
  execute features and scenarios which do *not* have the given tag.

You should be able to use all the other Nose features, like coverage or profiling for "free". You
can also run all your unit, doctests, and Freshen tests in one go. Please consult the `Nose manual`_
for more details.


Additional notes
----------------

**Why copy Cucumber?** - Because it works and lots of people use it. Life is short, so why spend it
on coming up with new syntax for something that already exists?

**Why use Nose?** - Because it works and lots of people use it and it already does many useful
things. Life is short, so why spend it reimplementing coverage, profiling, test discovery, and
command like processing again?

**Can I contribute?** - Yes, please! While the tool is currently a copy of Cucumber's syntax,
there's no law that says it has to be that forever. If you have any ideas or suggestions (or bugs!),
please feel free to let me know, or simply clone the repo and play around.

.. _`Nose`: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/
.. _`Nose manual`: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
.. _`Cucumber`: http://cukes.info
.. _`Source code`: http://github.com/rlisagor/freshen


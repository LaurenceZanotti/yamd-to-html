# Yet another Markdown to HTML converter

`yamd-to-html` converter is a module that converts `Markdown` to `HTML`. Originally wrote for Harvard's CS50 Web Programming course.

## How to use it

1. Download and save the code in your project directory.
2. Import it and use it:

        from path/to/the/module import Converter
   
        md = Converter(your_markdown_content)
        html = md.convertHTML()

## Motivation

In one of the projects of [Harvard's CS50 Web course](https://cs50.harvard.edu/web), the students are challenged to create a `Markdown` to `HTML` converter of their own using regular expressions, if they wish.

Even though the staff recommends [`python-markdown2`](https://github.com/trentm/python-markdown2), I was feeling comfortable to take this challenge and saw an opportunity to learn about regular expressions and object oriented programming, practicing it more.

## Contributions

The code was designed thinking specifically for that [project's specifications](https://cs50.harvard.edu/web/2020/projects/1/wiki/#specification), and was one of my first tries to create an independent piece of code for a specific functionality, so this might have limited the potential of the general idea (or not). 

The project doesn't really have a goal still, but any feedback or contribution is very appreciated. Might look into package distribution and support up next.

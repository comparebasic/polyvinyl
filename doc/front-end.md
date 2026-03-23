# PolyVinyl Frontend

The frontned framework is a small set of JavaScript utilities that follow the configuration json for the backend to create interactive websites.


## Components of the FrontEnd

- [utils.form](/polyvinyl/utils/form.py) (python) is the Python module that interprets configuration and generates the HTML and JavaScript bindings.
- [ui/form.js](/ui/form.js) is the JavaScript utility that takes the configuration and makes it interactive

## Python Form Module - `utils.form` 

The configuration file is discussed in the [ui](/doc.ui.md) section of the documentation, which discusses the backend HTML generation as well.

## JavasScript Form Binding - `form.js`

The JavaScript loads up with the page and is then called from a script just below each HTML Form element.

### Functions of `form.js`

#### Main Closure

```JavaScript
(function(){
    if(typeof window._polyvinyl === "undefined"){
        window._polyvinyl = {}
    }

    if(typeof window._polyvinyl.Form !== "undefined"){
        return
    }

    //.. stuff

    /* publicly accessible JavaScript objects */
    window._polyvinyl.Form = {
        register,
        list: [],
    }
})()
```

This is a javascript module which wires up events and behaviour for validating
and showing users the status of thier progress filling out a form within a
webpage.

It is one large self-executing closer. The exposed objects are declared at the
bottom of this file.

#### _validateRules

```JavaScript
function _validateRules(content, rules){
```

Run through the regex array, this is valuable because the
descriptions have a corresponding array of elements that can be
styled to indicate failure in those matches


#### Show Description (errors)

```JavaScript
function showDesc(broke){
```

Highlihgt the specific description responsible that has violated a
validation match 


#### Validate Rules

```JavaScript
function validateRules(e, fully){
```

Validate a form input that has pattern matching rules

#### Validate Values

```JavaScript
function validateValue(e, fully){
```

Validate a form input that does not have pattern matching rules

#### Validate CheckBoxes and Radio Groups 
```
    function validateChecked(e, fully){
```

Validate a checkbox or radio group 


#### Validate Latest

```JavaScript
function validateLatest(e){
```
This is called every time a new element is focused.

The reason this exists is to make sure that users
are not interrupted with suggestions or errors before
they have had a chance to finish filling in an input.


#### Check Visibliity (for optional inclusion in form validity)

```JavaScript
function checkVisible(){
```

This makes sure that a form input is visible, so
that only visible elements are considered for validation.
This is becuase optional elements that are hidden do
not need to be considered 

#### Validate Button

```JavaScript
function validateButton(e){
```

Make sure the button is part of a form that is ready to submit
preventing the event from submitting the page unless the form
is ready
         

#### Validate Form

```JavaScript
function validateForm(){
```

Loop through the inputs and verify if they are either:

1. required
2. visible
3. invalid

If all three are true the form is not valid, but if a non-required
or non-visible input is not valid that does not invalidate the form 

Note: all fields are responsible for tracking their validatio stat,
validation is not run from this, but derives existing validity from
the field objects


#### Make Field

```JavaScript
function makeField(el, config, form){
```

Create a field object that will be attached to the Element, and
setup the events

This function chooses which DOM events to connect to the element,
and which validation function to connect to the element.

These decisions are made by a combination of the Element type
attribute and the configuration entries for the element

Elements with type "radio" are treated in a special way, they do not
get unique `_ui` objects, and the `el` property becomes an array of
elements instead of a single one, so that they can be grouped
together (which is what radio buttons are for).


#### Register (form)

```JavaScript
function register(jsid, config){
```

Using a configuration, setup the elements of an HTML Form element

This assumes that the forms are present and loaded on the page.

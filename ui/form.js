/*
Copyright (c) 2026 Compare Basic Incorporated
Open source under a BSD Three-Clause License

See the LICENCE file distributed with the publication of this source code for details


PolyVinyl UI

This is a javascript module which wires up events and behaviour for validating
and showing users the status of thier progress filling out a form within a
webpage.

It is one large self-executing closer. The exposed objects are declared at the
bottom of this file.

*/

(function(){
    if(typeof window._polyvinyl === "undefined"){
        window._polyvinyl = {}
    }

    if(typeof window._polyvinyl.Form !== "undefined"){
        return
    }

    const noop = function(){}

    function _validateRules(content, rules){
        /* Run through the regex array, this is valuable because the
         * descriptions have a corresponding array of elements that can be
         * styled to indicate failure in those matches */
        let i = 0
        for(; i < rules.length; i++){
            const re = rules[i]
            if(re && !re.test(content)){
                return i
            }
        }
        if(i == rules.length){
            return -1
        }
    }

    function showDesc(broke){
        /* Highlihgt the specific description responsible that has violated a
         * validation match */
        if(this._ui.desc_el){
            const length = this._ui.desc_el.childNodes.length
            for(let i = 0; i < length; i++){
                const desc = this._ui.desc_el.childNodes.item(i)
                if(i == broke){
                    desc.classList.add("broken")
                }else{
                    desc.classList.remove("broken")
                }
            }
        }
    }

    function validateRules(e, fully){
        /* Validate a form input that has pattern matching rules */
        let start = this._ui.is.valid
        const broke = _validateRules(this.value, this._ui.fieldConfig.rules)
        if(broke === -1){
            this.parentNode.classList.add("valid")
            this.parentNode.classList.remove("invalid")
            this._ui.is.valid = true
        }else{
            this.parentNode.classList.remove("valid")
            this._ui.is.valid = false 
            if(fully){
                this.parentNode.classList.add("invalid")
                showDesc.call(this, broke)
            }else if(this.parentNode.classList.contains("invalid")){
                showDesc.call(this, broke)
            }
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate()
        }
    }

    function validateValue(e, fully){
        /* Validate a form input that does not have pattern matching rules */
        let start = this._ui.is.valid
        if(this.value){
            this.parentNode.classList.add("valid")
            this.parentNode.classList.remove("invalid")
            this._ui.is.valid = true
        }else{
            this.parentNode.classList.remove("valid")
            this._ui.is.valid = false 
            if(fully){
                this.parentNode.classList.add("invalid")
                showDesc.call(this, 0)
            }
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate()
        }
    }

    function validateChecked(e, fully){
        /* validate a checkbox or radio group */
        let start = this._ui.valid;
        let valid = false;
        if(this._ui.el instanceof Element && this.checked){
            valid = true
        }else{
            for(let i = 0; i < this._ui.el.length; i++){
                if(this._ui.el[i].checked){
                    valid = true
                    break;
                }
            }
        }

        this._ui.is.valid = valid 
        if(!valid && this._ui.is.required){
            showDesc.call(this, 0)
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate()
        }
    }

    function validateLatest(e){
        /* This is called every time a new element is focused.
         *
         * The reason this exists is to make sure that users
         * are not interrupted with suggestions or errors before
         * they have had a chance to finish filling in an input
         */
        if(this._ui.form._latest && this._ui.form._latest !== this){
            this._ui.form._latest.validate(e, true)
        }
        this._ui.form._latest = this
    }

    function checkVisible(){
        /* This makes sure that a form input is visible, so
         * that only visible elements are considered for validation.
         * This is becuase optional elements that are hidden do
         * not need to be considered 
         */
        const par = this.parentNode.parentNode
        if(par && par.classList.contains("optional")){
            const nodes = par.parentNode.childNodes;
            for(let i = 0; i < nodes.length; i++){
                if(nodes[i] == par){
                    break;
                }
                if(nodes[i].nodeName === "INPUT" && nodes[i].checked){
                    return true
                }
            }
            return false;
        }
        return this.getBoundingClientRect().height > 0
    }

    function validateButton(e){
        /* Make sure the button is part of a form that is ready to submit
         * preventing the event from submitting the page unless the form
         * is ready
         */
        validateLatest.call(this, e)
        if(!this._ui.is.valid){
            e.stopPropagation()
            e.preventDefault()
            return false
        }
    }

    function validateForm(){
        /* Loop through the inputs and verify if they are either:
         * 1. required
         * 2. visible
         * 3. invalid
         *
         * If all three are true the form is not valid, but if a non-required
         * or non-visible input is not valid that does not invalidate the form 
         *
         * Note: all fields are responsible for tracking their validatio stat,
         * validation is not run from this, but derives existing validity from
         * the field objects
         */
         */
        let i = 0
        for(; i < this.inputs.length; i++){
            const field = this.inputs[i]
            let visible = true 
            let debugName = "";
            if(field.el instanceof Element){
                debugName = field.el.getAttribute("name")
                visible = field.el.checkVisible()
            }else{
                for(let i = 0; i < field.el.length; i++){
                    let el = field.el[i]
                    debugName = el.getAttribute("name")
                    if(!el.checkVisible()){
                        visible = false
                        break
                    }
                }
            }

            if(field.is.required && visible && !field.is.valid){
                break
            }
        }
        const valid = i === this.inputs.length
        let cls = "invalid"
        let oldCls = "valid"
        if(valid){
            cls = "valid"
            oldCls = "invalid"
        }

        for(let i = 0; i < this.buttons.length; i++){
            this.buttons[i].is.valid = valid
            this.buttons[i].el.classList.add(cls)
            this.buttons[i].el.classList.remove(oldCls)
        }
    }

    function makeField(el, config, form){
        /* Create a field object that will be attached to the Element, and
         * setup the events
         *
         * This function chooses which DOM events to connect to the element,
         * and which validation function to connect to the element.
         *
         * These decisions are made by a combination of the Element type
         * attribute and the configuration entries for the element
         *
         * Elements with type "radio" are treated in a special way, they do not
         * get unique _ui objects, and the "el" property becomes an array of
         * elements instead of a single one, so that they can be grouped
         * together (which is what radio buttons are for).
         */
        const name = el.getAttribute("name")
        const type = el.getAttribute("type")

        const fieldConfig = config[name]
        let required = false
        let valid = false
        let validate = noop 
        let events = []
        let selectEvents = []
        let desc_el = null

        if(el.nodeName == "INPUT"){
            selectEvents.push("focus")
            if({"password":true, "text":true, "textarea": true}[type]){
                events.push("keyup")
                validate = validateValue
            }else if({"radio":true, "checkbox":true}[type]){
                events.push("change")
                validate = validateChecked
            }

            if(type == "password"){
                const eyes = el.parentNode.getElementsByClassName("eye")
                if(eyes && eyes.length){
                    (function(pw){
                        eyes[0].onclick = function(){
                            if(pw.classList.contains("visible-password")){
                                pw.classList.remove("visible-password")
                                pw.setAttribute("type", "password")
                                this.classList.remove("active")
                            }else{
                                pw.classList.add("visible-password")
                                pw.setAttribute("type", "text")
                                this.classList.add("active")
                            }
                        }
                    })(el)
                }
            }
        }else if(el.nodeName == "BUTTON"){
            events.push("click") 
            validate = validateButton
        }

        if(fieldConfig){
            required = true

            if(fieldConfig.rules){
                 for(let ii = 0; ii < fieldConfig.rules.length; ii++){
                      if(fieldConfig.rules[ii]){
                          fieldConfig.rules[ii] = new RegExp(fieldConfig.rules[ii])
                      }
                  }
                  if(validate === validateValue){
                      validate = validateRules
                  }
            }

            if(fieldConfig.description){
                desc_el = document.createElement("P")
                for(let i = 0; i < fieldConfig.description.length; i++){
                    const part = document.createElement("SPAN")
                    part.append(document.createTextNode(fieldConfig.description[i]))
                    desc_el.append(part)
                }
                desc_el.classList.add("val-description")
                el.parentNode.after(desc_el)
            }
        }

        for(let i = 0; i < events.length; i++){
            el.addEventListener(events[i], validate)
        }

        for(let i = 0; i < selectEvents.length; i++){
            el.addEventListener(selectEvents[i], validateLatest)
        }
       
        el.validate = validate
        el.checkVisible = checkVisible

        if(type === "radio"){
            if(form.radios[name]){
                const _ui = form.radios[name]
                if(_ui.el instanceof Element){
                    _ui.el = [_ui.el, el]
                }else{
                    _ui.el.push(el)
                }
                el._ui = _ui
                return _ui
            }
        }

        el._ui = {
            el,
            desc_el,
            is: {
                valid,
                required
            },
            fieldConfig,
            form
        }

        if(type === "radio"){
            form.radios[name] = el._ui
        }

        return el._ui
    }

    function register(jsid, config){
        /* Using a configuration, setup the elements of an HTML Form element
         *
         * This assumes that the forms are present and loaded on the page.
         */
         const form_el = document.getElementById(jsid)
         if(form_el){
             let valid = false
             const form = {
                el: form_el,
                jsid,
                config,
                buttons: [],
                inputs: [],
                radios: {},
                validate: noop,
                is: {
                    valid
                },
                _latest: null,
             }

             let nodes = form_el.getElementsByTagName("BUTTON")
             let l = nodes.length
             for(let i = 0; i < l; i++){
                const field = makeField(nodes[i], config, form)
                if(field){
                    form.buttons.push(field)
                }
             }

             nodes = form_el.getElementsByTagName("INPUT")
             l = nodes.length
             for(let i = 0; i < l; i++){
                  const el = nodes[i]
                  form.inputs.push(makeField(el, config, form))
                  if(typeof el.validate !== "undefined"){
                      el.validate()
                  }
             }
             
             form.validate = validateForm
             form.validate()
             this.list.push(form)
         }
    }

    /* publicly accessible JavaScript objects */
    window._polyvinyl.Form = {
        register,
        list: [],
    }
})()

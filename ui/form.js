(function(){
    if(typeof window._polyvinyl === "undefined"){
        window._polyvinyl = {}
    }

    if(typeof window._polyvinyl.Form !== "undefined"){
        return;
    }

    const noop = function(){}

    function _validateRules(content, rules){
        let i = 0;
        for(; i < rules.length; i++){
            const re = rules[i];
            if(re && !re.test(content)){
                return i;
            }
        }
        if(i == rules.length){
            return -1;
        }
    }

    function showDesc(broke){
        if(this._desc_el){
            const length = this._desc_el.childNodes.length;
            for(let i = 0; i < length; i++){
                const desc = this._desc_el.childNodes.item(i);
                if(i == broke){
                    desc.classList.add("broken"); 
                }else{
                    desc.classList.remove("broken"); 
                }
            }
        }
    }

    function validateRules(e, fully){
        let start = this._ui.is.valid
        const broke = _validateRules(this.value, this._ui.fieldConfig.rules)
        if(broke === -1){
            this.parentNode.classList.add("valid")
            this.parentNode.classList.remove("invalid")
            this._ui.is.valid = true
        }else{
            this.parentNode.classList.remove("valid")
            if(fully){
                this.parentNode.classList.add("invalid")
                showDesc.call(this, broke);
                this._ui.is.valid = false 
            }
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate()
        }
    }

    function validateValue(e, fully){
        let start = this._ui.is.valid
        if(this.value){
            this.parentNode.classList.add("valid")
            this.parentNode.classList.remove("invalid")
            this._ui.is.valid = true
        }else{
            this.parentNode.classList.remove("valid")
            if(fully){
                this.parentNode.classList.add("invalid")
                showDesc.call(this, 0);
                this._ui.is.valid = false 
            }
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate()
        }
    }

    function validateChecked(e, fully){
        let start = this._ui.is.valid
        console.log(start, this)
        console.log(start, this.value)
        console.log(start, this.checked)
        if(this.checked){
            this._ui.is.valid = true;
        }else{
            this._ui.is.valid = false;
            if(this._ui.is.required){
                showDesc.call(this, 0)
            }
        }

        if(start !== this._ui.is.valid){
            this._ui.form.validate();
        }
    }

    function validateLatest(e){
        if(this._ui.form._latest && this._ui.form._latest !== this){
            this._ui.form._latest.validate(e, true)
        }
        this._ui.form._latest = this;
    }

    function checkVisible(){
        return this.getBoundingClientRect().height > 0;
    }

    function validateButton(e){
        validateLatest.call(this, e);
        if(!this.is.valid){
            e.stopPropagation();
            e.preventDefault();
            return false;
        }
    }

    function validateForm(){
        let i = 0
        for(; i < this.inputs.length; i++){
            const field = this.inputs[i]
            console.log("Field " + field.el.getAttribute("name") + 
                ", Required " + field.is.required +
                ", Visible " + field.el.checkVisible() +
                ", Valid " + field.is.valid,
            field.el)
                
            if(field.is.required && field.el.checkVisible() && !field.is.valid){
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

        console.log("form valid ?", valid);

        for(let i = 0; i < this.buttons.length; i++){
            console.log(this.buttons[i])
            this.buttons[i].is.valid = valid
            this.buttons[i].el.classList.add(cls)
            this.buttons[i].el.classList.remove(oldCls)
        }
    }

    function makeField(el, config, form){
        const name = el.getAttribute("name")
        const type = el.getAttribute("type")
        const fieldConfig = config[name];
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

        return el._ui;
    }


    function register(jsid, config){
         const form_el = document.getElementById(jsid)
         if(form_el){
             let valid = false
             const form = {
                el: form_el,
                jsid,
                config,
                buttons: [],
                inputs: [],
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
                form.buttons.push(field)
             }

             nodes = form_el.getElementsByTagName("INPUT")
             l = nodes.length
             for(let i = 0; i < l; i++){
                  const el = nodes[i];
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

    window._polyvinyl.Form = {
        register,
        list: [],
    }

})();

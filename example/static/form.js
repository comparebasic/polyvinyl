(function(){
    if(typeof window._polyvinyl === "undefined"){
        window._polyvinyl = {}
    }

    if(typeof window._polyvinyl.form !== "undefined"){
        return;
    }

    let inp_li = document.getElementsByTagName("input");
    let len = inp_li.length;
    const by_name = {};
    for(let i = 0; i < len; i++){
        inp = inp_li[i];
        by_name[inp.getAttribute("name")] = inp;
    } 

    for(let i = 0; i < len; i++){
        inp = inp_li[i];
        if(inp.getAttribute("type") == "checkbox"){
            let disableName = inp.getAttribute("data-disable");
            if(disableName){
                (function(disableInput){
                    inp.onclick = function(){
                        disableInput.disabled = this.checked;
                        console.log(disableInput);
                    }
                })(by_name[disableName]);
            }
        }
    }

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

    function validateKeyPress(e){
        if(this._validation){
            const broke = _validateRules(this.value, this._val.rules);
            if(broke === -1){
                this.parentNode.classList.add("valid");
                this.parentNode.classList.remove("invalid");
            }else{
                this.parentNode.classList.remove("valid");
            }
        }
    }

    function validateLast(e){
        if(this._validation && typeof this._validation.form._latest !== "undefined" && this._validation.form._latest !== this){
            const node = this._validation.form._latest;
            console.log(node);

            if(node._val){
                const broke = _validateRules(node.value, node._val.rules);
                if(broke == -1){
                    node.parentNode.classList.remove("invalid");
                }else{
                    node.parentNode.classList.add("invalid");
                    if(node._desc_el){
                        const length = node._desc_el.childNodes.length;
                        for(let i = 0; i < length; i++){
                            const desc = node._desc_el.childNodes.item(i);
                            if(i == broke){
                                desc.classList.add("broken"); 
                            }else{
                                desc.classList.remove("broken"); 
                            }
                        }
                    }
                }
            }
        }
        this._validation.form._latest = this;
    }

    function register(jsid, validation){
         validation.form = document.getElementById(jsid);
         this.elems[jsid] = {
              validation,
         }

         const buttons = validation.form.getElementsByTagName("BUTTON");
         let l = buttons.length;
         for(let i = 0; i < l; i++){
              const btn = buttons[i];
              btn.addEventListener("focus",validateLast);
              btn.addEventListener("click",validateLast);
         }

         const inputs = validation.form.getElementsByTagName("INPUT");
         l = inputs.length;
         for(let i = 0; i < l; i++){
              const inp = inputs[i];

              inp._validation = validation;
              inp.addEventListener("focus",validateLast);
              inp.addEventListener("click",validateLast);

              const name = inp.getAttribute("name");
              if(validation[name]){
                  val = validation[name];
                  for(let ii = 0; ii < val.rules.length; ii++){
                      if(val.rules[ii]){
                          val.rules[ii] = new RegExp(val.rules[ii]);
                      }
                  }
                  inp._val = val;
                  inp.addEventListener("keyup",validateKeyPress);

                  const desc = document.createElement("P");
                  for(let ii = 0; ii < val.description.length; ii++){
                      const part = document.createElement("SPAN");
                      part.append(document.createTextNode(val.description[ii]));
                      desc.append(part);
                  }
                  desc.classList.add("val-description");
                  inp.parentNode.after(desc);
                  inp._desc_el = desc;
              }

              if(inp.getAttribute("type") === "password"){
                    let node = inp;
                    while(node){
                        node = node.nextSibling; 
                        if(node && node.classList.contains("eye")){
                            (function(pwinp){
                                node.onclick = function(){
                                    console.log("Oop");
                                    if(pwinp.classList.contains("visible-password")){
                                        pwinp.classList.remove("visible-password");
                                        this.classList.remove("active");
                                        pwinp.setAttribute("type", "password");
                                    }else{
                                        pwinp.classList.add("visible-password");
                                        this.classList.add("active");
                                        pwinp.setAttribute("type", "text");
                                    }
                                }
                            })(inp);
                        }
                    }
              }
         }
    }

    window._polyvinyl.form = {
        register,
        elems: {}
    }

})();

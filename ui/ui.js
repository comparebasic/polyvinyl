(function(){
    const MAJOR = 4;

    if(typeof window._polyvinyl === "undefined"){
        window._polyvinyl = {}
    }

    if(typeof window._polyvinyl.Editor !== "undefined"){
        return
    }else{
        window._polyvinyl.Editor = {}
    }

    function err(e){
        throw new Error("Error loading data", e)
    }   

    if (typeof window._ui == "undefined"){
        window._ui = {
            views: [] 
        }
    }

    const stash = document.getElementById("stash");
    const stage = document.getElementsByClassName("editor-ui")[0];

    function makeSvg(el, w, h){
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            console.log(svg);
            svg.setAttribute('width', w);
            svg.setAttribute('height', h);
            svg.setAttributeNS("http://www.w3.org/2000/xmlns/",
                "xmlns:xlink", "http://www.w3.org/1999/xlink");
            el.appendChild(svg);
        return svg;
    }

    function drawGrid(){
        const box = this.el.getBoundingClientRect();
        console.log(box);
        this.svg = makeSvg(el, box.width, box.height);
        const inc = 20 * this.scale;
        let pos = 0;
        let x = 0;
        let y = 0;
        let i = 0;
        while(y < box.height){
            const line = document.createElementNS("http://www.w3.org/2000/svg", 'path');
            const d = `M 0 ${y} L ${box.width} ${y}`;
            line.setAttribute("d", d);
            if(++i % MAJOR == 0){
                line.setAttribute("stroke-width", 1);
                line.setAttribute("stroke", "#888");
            }else{
                line.setAttribute("stroke-width", 1);
                line.setAttribute("stroke", "#AAA");
            }
            this.svg.append(line);
            y += inc;
        }
        while(x < box.width){
            const line = document.createElementNS("http://www.w3.org/2000/svg", 'path');
            const d = `M ${x} 0  L ${x} ${box.height}`
            line.setAttribute("d", d);
            if(++i % MAJOR == 0){
                line.setAttribute("stroke-width", 1)
                line.setAttribute("stroke", "#888")
            }else{
                line.setAttribute("stroke-width", 1)
                line.setAttribute("stroke", "#AAA")
            }
            this.svg.append(line)
            x += inc;
        }
    }

    function setScale(value){
        this.scale = value
        console.log(this.scale)
        console.log(this.svg)
        this.svg.setAttribute("transform", `scale(${this.scale})`)
    }

    function positionTool(el, x, y){
        el.style.top = x + 'px';
        el.style.left = y + 'px';
    }

    const toolbarMap = {
        "new": function(el){
            el.addEventListener("click", function(){
                console.log("clicked new", el)
            });
        }
    }

    function wireUp(el, map){
        const actions = el.getElementsByTagName("A");
        const length = actions.length;
        for(let i = 0; i < length; i++){
            let a = actions[i];
            let name = a.getAttribute("data:name");
            if(map[name]){
                map[name](el)
            }
        }
    }

    function init(){
        const editors = document.getElementsByClassName("editor-ui")
        const len = editors.length
        for(let i = 0; i < len; i ++){
            el = editors[i]
            console.log(el)
            if(typeof el._meta == "undefined"){
                el._meta = {
                    scale: 1.0,
                    drawGrid,
                    setScale,
                    el,
                }
            }
            el._meta.drawGrid()
            window._ui.views.push(el._meta)
        }

        window.onkeypress = function(e){
            console.log(e);
            if(e.key == "+"){
                for(let i = 0; i < window._ui.views.length; i++){
                    const v = window._ui.views[i];
                    v.setScale(v.scale*1.1);
                }
            }else if(e.key == "-"){
                for(let i = 0; i < window._ui.views.length; i++){
                    const v = window._ui.views[i];
                    v.setScale(v.scale*0.9);
                }
            }
        }

        const toolbar = stash.getElementsByClassName("editor-toolbar")[0].cloneNode(true)
        wireUp(toolbar, toolbarMap);
        stage.append(toolbar);
        positionTool(toolbar, 50, 50);
    }

    fetch("/api/handlers.json").then(function(resp){
        resp.json().then(function(h){
            window._polyvinyl.Editor.handlers = h
            console.log(h)
        }, err)
    }, err);

    init();
})();

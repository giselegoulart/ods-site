window.addEventListener('load', uploadFormScriptInit)

function mScriptInit(){
    const mButton = [document.querySelector('#toggle'), document.querySelector('#dropButton')],
    mMenu = document.querySelector('.mNav'),
    mButtonIcon = document.querySelector('#toggle'),
    mailButton = document.querySelector('#mailButton'),
    mailModal = document.querySelector('#contactForm'),
    mailModalWrap = document.querySelector('#mailWrapper'),
    mailModalClose = document.querySelector('#contactFormClose');

    // Objects pertaining to the ClassWatcher class act by keeping track of any changes on the specified HTML element`s classlist and acting upon such changes.

    class ClassWatcher {

        constructor(targetNode, classToWatch, classAddedCallback, classRemovedCallback) {
            this.targetNode = targetNode
            this.classToWatch = classToWatch
            this.classAddedCallback = classAddedCallback
            this.classRemovedCallback = classRemovedCallback
            this.observer = null
            this.lastClassState = targetNode.classList.contains(this.classToWatch)

            this.init()
        }

        init() {
            this.observer = new MutationObserver(this.mutationCallback)
            this.observe()
        }

        observe() {
            this.observer.observe(this.targetNode, { attributes: true })
        }

        disconnect() {
            this.observer.disconnect()
        }

        mutationCallback = mutationsList => {
            for(let mutation of mutationsList) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    let currentClassState = mutation.target.classList.contains(this.classToWatch)
                    if(this.lastClassState !== currentClassState) {
                        this.lastClassState = currentClassState
                        if(currentClassState) {
                            this.classAddedCallback()
                        }
                        else {
                            this.classRemovedCallback()
                        }
                    }
                }
            }
        }
    }

    const classWatcher = new ClassWatcher(mMenu, 'active', classadd, classrem);

    mButton.forEach(function(i){i.addEventListener("click", function() {mMenu.classList.toggle('active');;});})

    mailButton.addEventListener("click", function(){mailModal.classList.toggle('active'); mailModalWrap.classList.toggle('active');});
    mailModalClose.addEventListener("click", function(){mailModal.classList.toggle('active'); mailModalWrap.classList.toggle('active');});

    function classadd(){
        if (mButtonIcon.checked != true){
            mButtonIcon.checked = true;
        }
    }

    function classrem() {
        if (mButtonIcon.checked != false){
            mButtonIcon.checked = false;
        }
    }
};mScriptInit();


function onScrollAnimationInit() {
    try{
        const targetDivs = document.querySelectorAll('.js-animate')
        targetDivs[0].classList.add('active')
        

        function animateOnView() {
            targetDivs.forEach((i,index) => {
                const targetOffsetTop = i.getBoundingClientRect().top
                const viewParameter = window.innerHeight*.65
                const isOnView = targetOffsetTop <= viewParameter
                // console.log(`Div ${index} offset from top: ${targetOffsetTop}`)
                // console.log(viewParameter)
                if(isOnView) {
//                    console.log('On view')
                    i.classList.add('active')
                }
//                else console.log('Not on view')
            })
        }

        window.addEventListener('scroll', animateOnView)
    }
    catch (e){
        console.log(e + 'Erro scroll')
    }
};onScrollAnimationInit();

function uploadFormScriptInit(){
    const form = document.querySelector(".upload"),
    fileInput = document.querySelector(".file-input"),
    progressArea = document.querySelector(".progress-area"),
    uploadedArea = document.querySelector(".uploaded-area"),
    sendButton = document.querySelector('.send button');
    console.log(form)
    let fileSize = [],
    fileName = [],
    progressHTML,
    uploadedHTML;

    // Right now the file upload interface only works with single changes to the form.
    // E.g.: the user cannot choose which files to upload more than once, nor can
    // they add more files to the list of files that they had previously selected.

    // form click event
    if (form){
        form.addEventListener("click", () =>{
            fileInput.click();
        });

        sendButton.onclick = (e) => {
            e.preventDefault()
            fileInput.removeAttribute('disabled')
            form.submit()
        }
    
        fileInput.onchange = ({target})=>{
            console.log(target.files)
            fileInput.setAttribute('disabled', '')
            for (i=0; i<target.files.length; i++){
                let file = target.files[i]; //getting file [0] this means if user has selected multiple files then get first one only
                if(file){
                    console.log(file.size)
                    fileSize.push(file.size); //getting file size
                    // if file size is less than 1024 then add only KB else convert this KB into MB
                    (fileSize[i] < 1024) ? fileSize[i] = fileSize[i] + " KB" : fileSize[i] = (fileSize[i] / (1024*1024)).toFixed(2) + " MB";
                    fileName.push(file.name); //getting file name
                    if(fileName[i].length >= 12){ //if file name length is greater than 12 then split it and add ...
                        let splitName = fileName[i].split('.');
                        fileName[i] = splitName[0].substring(0, 13) + "... ." + splitName[1];
                    }
                }
            }
            console.log(fileName, fileSize);
            for(i=0;i<target.files.length; i++){
//                progressHTML = `<li class="row">
//                                        <i class="fas fa-file-alt"></i>
//                                        <div class="content" >
//                                        <div class="details">
//                                            <span class="name">${fileName[i]}</span>
//                                            <span class="percent">${fileSize[i]}</span>
//                                        </div>
//                                        </div>
//                                    </li>`;
                
                // Possible progressArea with close button

                 progressHTML = `<li class="row">
                                         <i class="fas fa-file-alt"></i>
                                         <div class="content" >
                                         <div class="details">
                                             <span class="name">${fileName[i]}</span>
                                             <span class="percent">${fileSize[i]}</span>
                                             <span><i class="fa-solid fa-xmark clsBtn" id='${i}' style="cursor: pointer;"></i></span>
                                         </div>
                                         </div>
                                     </li>`;
                
                progressArea.innerHTML += progressHTML;
            }
            console.log(fileName, fileSize)
             progressArea.querySelectorAll(`.clsBtn`).forEach(i => {
                 i.addEventListener('click', e => {
//                     e.currentTarget.closest('li').remove()
//                     let index = e.currentTarget.getAttribute('id')
//                     fileName.splice(index, 1)
//                     fileSize.splice(index, 1)
//                     console.log(fileName, fileSize)
                       location.reload(true)
                 })
             })
            // uploadFile(fileName, fileSize); //calling uploadFile, passing file name as an argument
            console.log(progressArea.scrollHeight > progressArea.clientHeight)
            progressArea.scrollHeight > progressArea.clientHeight ? [progressArea, uploadedArea].forEach(i => i.classList.add('scroll')) : 
            [progressArea, uploadedArea].forEach(i => i.classList.remove('scroll'))
        }
    }
  
  // file upload function
  function uploadFile(names, sizes){
    let xhr = new XMLHttpRequest(); //creating new xhr object (AJAX)
    xhr.open("POST", "/upload/"); //sending post request to the specified URL
    xhr.upload.addEventListener("progress", ({loaded, total}) =>{ //file uploading progress event
      let fileLoaded = Math.floor((loaded / total) * 100);  //getting percentage of loaded file size
      progressHTML = `<li class="row">
                            <i class="fas fa-file-alt"></i>
                            <div class="content">
                              <div class="details">
                                <span class="name">${names.length === 1 ? `${names[0]} • Uploading` : "Enviando arquivos selecionados"}</span>
                                <span class="percent">${fileLoaded}%</span>
                              </div>
                              <div class="progress-bar">
                                <div class="progress" style="width: ${fileLoaded}%"></div>
                              </div>
                            </div>
                          </li>`;
      // uploadedArea.innerHTML = ""; //uncomment this line if you don't want to show upload history
      uploadedArea.classList.add("onprogress");
      progressArea.innerHTML = progressHTML;
      if(loaded == total){
        for (i=0;i<names.length;i++){
          progressArea.innerHTML = "";
          uploadedHTML = `<li class="row">
                                <div class="content upload">
                                  <i class="fas fa-file-alt"></i>
                                  <div class="details">
                                    <span class="name">${names[i]} • Enviado</span>
                                    <span class="size">${sizes[i]}</span>
                                  </div>
                                </div>
                                <i class="fas fa-check"></i>
                              </li>`;
          uploadedArea.classList.remove("onprogress");
          // uploadedArea.innerHTML = uploadedHTML; //uncomment this line if you don't want to show upload history
          uploadedArea.insertAdjacentHTML("afterbegin", uploadedHTML); //remove this line if you don't want to show upload history
        }
      }
    });
    sendButton.addEventListener("click", (e) => {
      let data = new FormData(form); //FormData is an object to easily send form data
      xhr.send(data); //sending form data
      data.forEach(i => {
        data.delete(i.name)
      })
      e.currentTarget.setAttribute("disabled", "")
      fileInput.setAttribute("disabled", "")
    })
  }
};

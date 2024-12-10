console.log("Tsting testing testing");

document.addEventListener('DOMContentLoaded', () => {
    const nextBtn = document.querySelectorAll('.next-btn');
    const previousBtn = document.querySelectorAll('.prev-btn');
    const steps = Array.from(document.querySelectorAll('.step'));
    const submitBtn = document.querySelector('.submit-btn')
    const form = document.querySelector('#form-wrapper');
    const totalStep = 8;

    console.log(`Number of steps: ${steps.length}`);
    let currentStep = steps.findIndex(step => {
        return step.classList.contains("active")
    })

    console.log(`Current active step is: ${currentStep}`)

    const progress = (value) => {
        document.getElementsByClassName('progress-bar')[0].style.width = `${value}%`;
    }
    
    previousBtn.forEach(button => {
        button.addEventListener('click', () => {
            console.log('Previous button clicked!');
            currentStep -= 1;
            console.log(`New step after clicked is: ${currentStep}`)
            moveStep();
            progress( (currentStep+1)/totalStep * 100 );
        });
    });

    nextBtn.forEach(button => {
        button.addEventListener('click', () => {
            console.log('Next button clicked!');
            currentStep += 1;
            console.log(`New step after clicked is: ${currentStep}`)
            moveStep();
            progress( (currentStep+1)/totalStep * 100 );
        });
    });

    function moveStep() {
        steps.forEach(step => step.classList.remove('active'));
        steps[currentStep].classList.add('active');
    }


    // form.addEventListener('submit', (e) => {
    //     e.preventDefault();
    //     const inputs = [];
    //     console.log('submitting')
    //     form.querySelectorAll("input").forEach((input) => {
    //         const {name,value} = input;
    //         inputs.push({name,value});
    //     });
    //     console.log('Submission: ',inputs);
    //     form.reset();
    // })

    form.addEventListener('submit', (e) => {
        e.preventDefault(); 
        const inputs = form.querySelectorAll('input:checked');
        console.log('Inputs selected:', inputs);
        const inputData = Array.from(inputs).map((input) => {
            console.log('Input name:', input.name, 'Input value:', input.value);
            return { name: input.name, value: input.value };
        });
        console.log('Final Submission Array:', JSON.stringify(inputData, null, 2));
        
        // Send the inputData array to Django to process by using AJAX
        // ref:  https://medium.com/@munyaokelvin/how-to-fetch-data-from-an-ajax-fetch-api-in-django-e825a329a36d 
        
        fetch('/skin-quiz/', {
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':csrftoken,
            },
            body: JSON.stringify({'post_data':inputData})
            })
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                console.log('Success: ',data);
            })
            .catch((error) => {
                console.error('Error: ',error);
            })
        form.reset();
    });
    
    function getToken(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            
            if (cookie.substring(0,name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
       }
       var csrftoken = getToken('csrftoken')


    submitBtn.addEventListener('click', () => {
        window.location.assign('quiz-result.html');
    })
    
});
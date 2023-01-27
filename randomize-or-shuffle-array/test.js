const questionaire = [
    {
        question: "A Thief is also known as___",
        category: "General",
        type: 'multiple',
        options: ['Criminal', 'Armed Robber', 'Doctor', 'Pirate'],
        answer: [0, 1, 3]
    },
    {
        question: 'Buhari is the current Nigeria President?',
        category: 'English',
        type: 'true-false',
        options: ['True', 'False'],
        answer: ["0"]
    },
    {
        question: 'Who owns Twitter?',
        category: 'English',
        type: 'single',
        options: ['Pius', 'Elon', 'Donald', 'Peter'],
        answer: [1]
    }
]


Array.prototype.shuffled = function () {
    const randomQuestionaire = [];
    while (randomQuestionaire.length < this.length) {
        let r = Math.floor(Math.random() * this.length);
        if (randomQuestionaire.indexOf(this[r]) === -1) {
            randomQuestionaire.push(this[r]);
        }
    }
    return randomQuestionaire
}

const shuffleOptions = function () {
    const oldQuestions = questionaire.shuffled()
    let newQuestions = []

    oldQuestions.forEach((el) => {
        let options = el.options;
        let answers = el.answer;


        let shuffledOption = [];
        let shuffledAns = []

        let temp = []
        for (let i = 0; i < options.length ; i++) {
            answers.forEach(ans => {
                if (ans == i) temp.push(options[i])
            })

            // if (answers.includes(i)){
            //     temp.push(options[i])
            // }
        }
        shuffledOption = options.shuffled();
        temp.forEach((value) => {
            shuffledAns.push(shuffledOption.indexOf(value))
        })

        el.options = shuffledOption
        el.answer = shuffledAns

        newQuestions.push(el)

    })
    return newQuestions
}

// Array.prototype.shuffleOption = function () {
//     const oldQuestions = questionaire.shuffled()
//     let newQuestions = []
//
//     oldQuestions.forEach((el) => {
//         let options = el.options;
//         let answers = el.answer;
//
//
//         let shuffledOption = [];
//         let shuffledAns = []
//
//         let temp = []
//         for (let i = 0; i < options.length ; i++) {
//             if (answers.includes(i)){
//                 temp.push(options[i])
//             }
//         }
//         shuffledOption = options.shuffled();
//         temp.forEach((value) => {
//             shuffledAns.push(shuffledOption.indexOf(value))
//         })
//
//         el.options = shuffledOption
//         el.answer = shuffledAns
//
//         newQuestions.push(el)
//
//     })
//     return newQuestions
// }


const t = shuffleOptions()

console.log(t)
console.log(t[0].answer)


// Array.prototype.shuffle = function() {
//     for (let i = 0; i < this.length; i++) {
//         let temp = ''.concat(this[i]);
//         let pos = Math.floor(Math.random() * this.length);
//         let other = ''.concat(this[pos]);
//         this[i] = other;
//         this[pos] = temp
//     }
//     return this
// }

//SINGLE ANSWER
// let myAns = undefined;
// let items = undefined;
// for (let i = 0; i < options.length ; i++) {
//     if (i === answer[0]){
//         let temp = []
//         myAns = options[i]
//         items = options.shuffle()
//         temp.push(items.indexOf(myAns))
//         myAns = temp
//     }
// }


// const n = [13, 24, 3, 5, 7, 8, 9, 11, 12, 13];
// const m = ['p', 't', 'h', 7, 8, 9];
//
// n.forEach((num1, index) => {
//     const num2 = m[index];
//     console.log(num1,);
//     console.log(num2);
// });
//

// console.log(questionaire.shuffled())
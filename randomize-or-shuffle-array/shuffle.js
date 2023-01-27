const questionaire = [
    {
        question: "A Thief is also known as___",
        category: "General",
        type: 'multiple',
        options: ['Criminal', 'Armed Robber', 'Doctor', 'Pirate'],
        answer: [0,1,3]
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


let options = questionaire[0].options
let myAnswer = questionaire[0].answer


let shuffledOption = [];
let shuffledOptionIndex = [];
let shuffledAns = []

let temp = []
for (let i = 0; i < options.length ; i++) {
    if (myAnswer.includes(i)){
        temp.push(options[i])
    }
}

shuffledOption = options.shuffled();
let optionIndex = options

temp.forEach((value) => {
    shuffledAns.push(shuffledOption.indexOf(value))
})

optionIndex.forEach((value) => {
    shuffledOptionIndex.push(shuffledOption.indexOf(value))
})


console.log(options)
console.log(myAnswer)

console.log(shuffledOption)
console.log(shuffledOptionIndex)
console.log(shuffledAns)


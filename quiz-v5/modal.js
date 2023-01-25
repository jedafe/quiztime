'use strict';

const modal = document.querySelector('.modal');
const overlay = document.querySelector('.overlay');
const btnShowModal = document.querySelector('.show-modal');
const btnCloseModal = document.querySelector('.close-modal');

const showModal = () => {
    modal.classList.remove('hidden');
    overlay.classList.remove('hidden');
}
const closeModal = () => {
    modal.classList.add('hidden');
    overlay.classList.add('hidden');
}


btnShowModal.addEventListener('click', showModal)

btnCloseModal.addEventListener('click', closeModal)
overlay.addEventListener('click', closeModal)

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !overlay.classList.contains('remove')) {
        closeModal();
    }
})
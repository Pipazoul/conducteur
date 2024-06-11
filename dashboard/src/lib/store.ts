import { writable } from 'svelte/store';
import { get } from 'svelte/store';
import { PUBLIC_ENV } from '$env/static/public'
let environment = PUBLIC_ENV || 'prod';
export const url = writable(environment === 'prod' ? '/' : 'http://localhost:8000/');
export const token = writable('');
export const users = writable([]);
export const predictions = writable([]);
export const tokens = writable([]);


export async function fetchUsers() {
    // url
    const response = await fetch(`${get(url)}users`, {
        headers: {
            Authorization: `Bearer ${get(token)}`,
        },
    });
    const data = await response.json();
    users.set(data);
}


export async function getPredictions() {
    console.log('getPredictions');
    console.log('token', get(token));
    try {
        const headers = new Headers();
        headers.set("Authorization", `Bearer ${get(token)}`);
        //const response = await fetch("http://localhost:8000/predictions", {
        const response = await fetch(get(url) + "predictions", {
            headers,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Get the current time and subtract 24 hours
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

        // Filter the predictions to only include those finished within the last 24 hours
        const filteredPredictions = data.filter(prediction => {
            const finishedTime = new Date(prediction.finished);
            return finishedTime >= oneDayAgo;
        });

        predictions.set(filteredPredictions);
    } catch (error) {
        console.error(error);
    }
}

export async function getTokens() {
    try {
        const headers = new Headers();
        headers.set("Authorization", `Bearer ${get(token)}`);
        //const response = await fetch("http://localhost:8000/predictions", {
        const response = await fetch(get(url) + "tokens", {
            headers,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        tokens.set(data);
    } catch (error) {
        console.error(error);
    }
}

export async function watch(){
    token.set(localStorage.getItem('token') || '');
    await fetchUsers();
    await getPredictions();
    await getTokens();

    // call watch every 5 seconds
    //setTimeout(watch, 5000);

}
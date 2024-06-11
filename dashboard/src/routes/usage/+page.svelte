<script lang="ts">
	import { users, url, token } from "../../lib/store";
    let currentUser = 0
    let predictions = []
    let images = new Set()
    let dateFilter = {
        '1d': 1,
        '1w': 7,
        '1m': 30,
        '3m': 90,
        '6m': 180,
        '1y': 365,
    }
    let currentFilter = '1d'


    $: {
        if($users.length > 0) {
            filter()
        }
    }

    async function filter() {
        // start is currentfiler 
        const end = new Date()
        const start = new Date(end.getTime() - dateFilter[currentFilter] * 24 * 3600 * 1000) 

        // convert to DD-MM-YYYY
        const startStr = `${start.getDate()}-${start.getMonth() + 1}-${start.getFullYear()}`
        const endStr = `${end.getDate()}-${end.getMonth() + 1}-${end.getFullYear()}`
        const res = await fetch(`${$url}user/predictions/`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${$token}`,
            },
            body: JSON.stringify({"user": $users[currentUser], "start": startStr, "end": endStr})
        })
        const data = await res.json()
        predictions = data
        console.log("LOL Predictions", predictions)
    }

    async function imageDuration() {
        // Create a new Set
        let imageSet = new Set();

        // For each prediction
        for (let i = 0; i < predictions.predictions.length; i++) {
            const prediction = predictions.predictions[i];

            // Check if the image already exists in the set
            let existingEntry = Array.from(imageSet).find(entry => entry.image === prediction.image);

            if (existingEntry) {
                // If it exists, update the sumDuration
                existingEntry.sumDuration += prediction.duration;
            } else {
                // If it doesn't exist, add a new entry to the set
                imageSet.add({
                    image: prediction.image,
                    sumDuration: prediction.duration
                });
            }
        }

        // Replace the old set with the new one
        images = imageSet;
    }
        

    function formatDuration(duration: number) {
        const hours = Math.floor(duration / 3600)
        const minutes = Math.floor((duration % 3600) / 60)
        const seconds = Math.round(duration % 60)

        let result = '';
        if (hours > 0) {
            result += `${hours}h `;
        }
        if (minutes > 0) {
            result += `${minutes}m `;
        }
        result += `${seconds}s`;

        return result.trim();
    }
</script>
<section>
    <h1>Usage</h1>
    <select class="select select-bordered" bind:value={currentUser} on:change={filter}>
        <option>Filter by user</option>
        {#each $users || [] as user, index}
            <option value={index}>{user}</option>
        {/each}
    </select>

    <select class="select select-bordered" bind:value={currentFilter} on:change={filter}>
        <option>Filter by duration</option>
        {#each Object.keys(dateFilter) as filter}
            <option value={filter}>{filter}</option>
        {/each}
    </select>
    <h2 class="mt-4">Overall Usage</h2>
    <div class="border rounded-md mt-4 p-4">
        Total duration: {formatDuration(predictions?.totalDuration)}

    </div>

</section>
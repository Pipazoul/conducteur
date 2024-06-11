<script lang="ts">
	import { config } from "$lib/store";
    $: console.log($config);

    function addToken() {
     
    }



</script>
<section>
    <div class="flex justify-between p-4 items-center">
        <h1>Tokens</h1>
        <button class="btn" on:click={addToken}>Add Token</button>
    </div>
    <div>
    {#each $config.tokens || [] as token, index}
        <div class="divider"></div>
        <div class="flex flex-col">
            <input type="text" class="input input-bordered input-xs w-full max-w-xs" bind:value={$config.tokens[index].name} />
            <input type="password" class="input input-bordered input-xs w-full max-w-xs" bind:value={$config.tokens[index].token} />
        </div>
        <h2>Scopes</h2>
        <div class="flex flex-col">
            <textarea class="textarea textarea-bordered w-full " rows="6" bind:value={$config.tokens[index].scope}></textarea>
        </div>
    {/each}
    </div>
</section>
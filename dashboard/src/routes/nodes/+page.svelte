<script lang="ts">
	import { nodesState } from "$lib/store";
    $: console.log($nodesState);

</script>
<section>
    <div class="flex justify-between p-4 items-center">
        <h1>Nodes</h1>
    </div>
    <div>
    {#if $nodesState?.length === 0 }
        <p>No nodes found</p>
    {:else}
        <div class="">
        {#each $nodesState || [] as node}
            <div class="border rounded-md mt-4 p-4 flex flex-col">
                <p>{node.name}</p>
                <p>{node.host}</p>
                {#if node.state === 'available'}
                    <div class="badge badge-primary">Available</div>
                {/if}
                {#if node.state === 'busy'}
                    <div class="badge badge-accent">
                        <span class="loading loading-spinner loading-xs"></span>
                        Busy
                    </div>
                {/if}
                {#if node.state === 'offline'}
                    <div class="badge badge-secondary">Offline</div>
                {/if}
            </div>
            {/each}
        </div>
    {/if}
    </div>
</section>

<script lang="ts">
  import "tailwindcss/tailwind.css";
  import { onMount } from "svelte";
	import { getTokens, watch, token, loadToken } from "../lib/store";

  onMount(async () => {
    await loadToken();
    if($token) {
      await watch();
      await getTokens();
    }
  });

  async function setToken(token: string) {
        localStorage.setItem('token', token);
        await watch();
        await getTokens();
    }
</script>
<div class="flex justify-end absolute right-4 top-4 z-10">
  <button class="btn" onclick="token_modal.showModal()">🔑</button>
</div>
<!-- Open the modal using ID.showModal() method -->
<dialog id="token_modal" class="modal">
  <div class="modal-box flex flex-col justify-center">
      <h3 class="font-bold text-lg">Enter your token</h3>
      <div class="space-x-2 mt-2">
          <input class="input input-bordered w-full max-w-xs" type="text" bind:value={$token} />
          <button class="btn" on:click={() => setToken($token)}>Submit</button>
      </div>
  </div>
  <form method="dialog" class="modal-backdrop">
      <button>close</button>
  </form>
</dialog>
<div class="drawer lg:drawer-open">
  <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col items-center justify-start">
    <label for="my-drawer-2" class="absolute left-4 top-4 btn btn-primary drawer-button lg:hidden">🍔</label>
    <div class="pt-20 lg:pt-4 w-full lg:pl-4">
      {#if $token}
      <slot />
      {:else}
      <h1 class="text-4xl font-bold text-center pt-8">Please enter your token</h1>
      {/if}
    </div>  
  </div> 
  <div class="drawer-side">
    <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label> 
    <ul class="menu p-4 w-44 min-h-full bg-base-200 text-base-content">
      <!-- Sidebar content here -->
      <li><a href="/dashboard"> 💼 Jobs</a></li>
      <li><a href="/nodes"> 💻 Nodes</a></li>
      <li><a href="/usage"> ⌛ Usage</a></li>
      <li><a href="/tokens"> 🔐 Tokens</a></li>
    </ul>
  
  </div>
</div>


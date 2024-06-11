
<script>
  import "tailwindcss/tailwind.css";
  import { onMount } from "svelte";
	import { getTokens, watch } from "../lib/store";

  onMount(async () => {
    await watch();
    await getTokens();
  });
</script>
<div class="drawer lg:drawer-open">
  <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col items-center justify-start">
    <label for="my-drawer-2" class="absolute left-4 top-4 btn btn-primary drawer-button lg:hidden">🍔</label>
    <div class="pt-20 lg:pt-4 w-full lg:pl-4">
      <slot />
    </div>  
  </div> 
  <div class="drawer-side">
    <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label> 
    <ul class="menu p-4 w-44 min-h-full bg-base-200 text-base-content">
      <!-- Sidebar content here -->
      <li><a href="/tokens"> 🔐 Tokens</a></li>
      <li><a href="/usage"> ☕️ Usage</a></li>
      <li><a href="/dashboard"> 💼 Jobs</a></li>
    </ul>
  
  </div>
</div>


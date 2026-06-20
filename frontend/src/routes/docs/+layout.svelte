<script lang="ts">
  import { beforeNavigate } from '$app/navigation';
  import { page } from '$app/stores';
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';
  let { children } = $props();

  let path = $derived($page.url.pathname);
  let isDeveloperGuide = $derived(path === '/docs/developer');
  let isAdminGuide = $derived(path === '/docs/admin');
  let isRestricted = $derived(isDeveloperGuide || isAdminGuide);

  beforeNavigate(({ cancel }) => {
    if (isRestricted && (!$isLoggedIn || !$isAdmin)) {
      cancel();
      window.location.href = '/docs/user';
    }
  });
</script>

{@render children()}

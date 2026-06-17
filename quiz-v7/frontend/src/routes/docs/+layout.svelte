<script lang="ts">
  import { beforeNavigate } from '$app/navigation';
  import { page } from '$app/stores';
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';

  $: path = $page.url.pathname;
  $: isDeveloperGuide = path === '/docs/developer';
  $: isAdminGuide = path === '/docs/admin';
  $: isRestricted = isDeveloperGuide || isAdminGuide;

  beforeNavigate(({ cancel }) => {
    if (isRestricted && (!$isLoggedIn || !$isAdmin)) {
      cancel();
      window.location.href = '/docs/user';
    }
  });
</script>

<slot />

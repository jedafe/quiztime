<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';
  import { translate } from '$lib/stores/i18n';
  import { goto } from '$app/navigation';

  let loading = $state(true);
  let error = $state('');

  let stats: any = $state(null);
  let users: any[] = $state([]);
  let usersTotal = $state(0);
  let usersPage = $state(1);
  let usersTotalPages = $state(1);
  let topQuizzes: any[] = $state([]);
  let topCreators: any[] = $state([]);

  // CRUD state
  let categories: any[] = $state([]);
  let subcategories: any[] = $state([]);
  let badgeDefs: any[] = $state([]);
  let allAttempts: any[] = $state([]);
  let attemptsTotal = $state(0);
  let attemptsPage = $state(1);
  let attemptsTotalPages = $state(1);

  // Category form
  let catFormName = $state('');
  let catEditing: any = $state(null);
  let catSubmitting = $state(false);
  let catError = $state('');

  // Subcategory form
  let subFormName = $state('');
  let subFormCategoryId = $state('');
  let subEditing: any = $state(null);
  let subSubmitting = $state(false);
  let subError = $state('');

  // Badge form
  let badgeFormKey = $state('');
  let badgeFormName = $state('');
  let badgeFormDesc = $state('');
  let badgeFormIcon = $state('');
  let badgeFormCriteria = $state('');
  let badgeEditing: any = $state(null);
  let badgeSubmitting = $state(false);
  let badgeError = $state('');

  // Delete confirm
  let deleteItem: any = $state(null);
  let deleteType = $state('');
  let deleteSubmitting = $state(false);

  let activeTab = $state<'overview' | 'users' | 'quizzes' | 'creators' | 'categories' | 'subcategories' | 'badges' | 'attempts'>('overview');

  onMount(async () => {
    if (!$isLoggedIn || !$isAdmin) {
      goto('/');
      return;
    }
    await loadData();
  });

  async function loadData() {
    loading = true;
    error = '';
    try {
      const [s, uq, uc] = await Promise.all([
        api.getAdminStats(),
        api.getAdminTopQuizzes(10),
        api.getAdminTopCreators(10),
      ]);
      stats = s;
      topQuizzes = uq;
      topCreators = uc;
      await loadUsers();
      await loadCategories();
    } catch (e: any) {
      error = e.message || 'Failed to load admin data';
    } finally {
      loading = false;
    }
  }

  async function loadUsers() {
    try {
      const res = await api.listAdminUsers(usersPage, 20);
      users = res.items;
      usersTotal = res.total;
      usersTotalPages = res.total_pages;
    } catch (e: any) {
      error = e.message || 'Failed to load users';
    }
  }

  async function changeRole(userId: string, role: string) {
    try {
      await api.changeUserRole(userId, role);
      await loadUsers();
    } catch (e: any) {
      error = e.message || 'Failed to change role';
    }
  }

  async function loadCategories() {
    try { categories = await api.adminListCategories(); } catch {}
  }
  async function loadSubcategories() {
    try { subcategories = await api.adminListSubcategories(); } catch {}
  }
  async function loadBadgeDefs() {
    try { badgeDefs = await api.adminListBadgeDefinitions(); } catch {}
  }
  async function loadAttempts() {
    try {
      const res = await api.adminListAttempts({ page: attemptsPage, pageSize: 20 });
      allAttempts = res.items;
      attemptsTotal = res.total;
      attemptsTotalPages = res.total_pages;
    } catch (e: any) { error = e.message; }
  }

  async function saveCategory() {
    catSubmitting = true; catError = '';
    try {
      if (catEditing) {
        await api.adminUpdateCategory(catEditing.id, { name: catFormName });
      } else {
        await api.adminCreateCategory({ name: catFormName });
      }
      catFormName = ''; catEditing = null;
      await loadCategories();
    } catch (e: any) { catError = e.message; }
    catSubmitting = false;
  }

  function editCategory(cat: any) {
    catEditing = cat;
    catFormName = cat.name;
  }

  function confirmDeleteCategory(cat: any) {
    deleteItem = cat;
    deleteType = 'category';
  }

  async function saveSubcategory() {
    subSubmitting = true; subError = '';
    try {
      if (subEditing) {
        await api.adminUpdateSubcategory(subEditing.id, { name: subFormName, category_id: subFormCategoryId });
      } else {
        await api.adminCreateSubcategory({ name: subFormName, category_id: subFormCategoryId });
      }
      subFormName = ''; subFormCategoryId = ''; subEditing = null;
      await loadSubcategories();
    } catch (e: any) { subError = e.message; }
    subSubmitting = false;
  }

  function editSubcategory(sub: any) {
    subEditing = sub;
    subFormName = sub.name;
    subFormCategoryId = sub.category_id;
  }

  function confirmDeleteSubcategory(sub: any) {
    deleteItem = sub;
    deleteType = 'subcategory';
  }

  async function saveBadge() {
    badgeSubmitting = true; badgeError = '';
    try {
      const data = {
        key: badgeFormKey,
        name: badgeFormName,
        description: badgeFormDesc,
        icon: badgeFormIcon,
        criteria: badgeFormCriteria ? JSON.parse(badgeFormCriteria) : {},
      };
      if (badgeEditing) {
        await api.adminUpdateBadgeDefinition(badgeEditing.id, data);
      } else {
        await api.adminCreateBadgeDefinition(data);
      }
      badgeFormKey = ''; badgeFormName = ''; badgeFormDesc = ''; badgeFormIcon = ''; badgeFormCriteria = ''; badgeEditing = null;
      await loadBadgeDefs();
    } catch (e: any) { badgeError = e.message; }
    badgeSubmitting = false;
  }

  function editBadge(b: any) {
    badgeEditing = b;
    badgeFormKey = b.key;
    badgeFormName = b.name;
    badgeFormDesc = b.description || '';
    badgeFormIcon = b.icon || '';
    badgeFormCriteria = JSON.stringify(b.criteria || {}, null, 2);
  }

  function confirmDeleteBadge(b: any) {
    deleteItem = b;
    deleteType = 'badge';
  }

  async function confirmDelete() {
    deleteSubmitting = true;
    try {
      if (deleteType === 'category') await api.adminDeleteCategory(deleteItem.id);
      else if (deleteType === 'subcategory') await api.adminDeleteSubcategory(deleteItem.id);
      else if (deleteType === 'badge') await api.adminDeleteBadgeDefinition(deleteItem.id);
      deleteItem = null; deleteType = '';
      await Promise.all([loadCategories(), loadSubcategories(), loadBadgeDefs()]);
    } catch (e: any) { error = e.message; }
    deleteSubmitting = false;
  }

  $effect(() => {
    if (activeTab === 'subcategories') loadSubcategories();
    else if (activeTab === 'badges') loadBadgeDefs();
    else if (activeTab === 'attempts') loadAttempts();
  });

  const tabs = $derived([
    { id: 'overview' as const, label: $translate('admin.overview') },
    { id: 'users' as const, label: $translate('admin.users') },
    { id: 'quizzes' as const, label: $translate('admin.quizzes') },
    { id: 'creators' as const, label: $translate('admin.creators') },
    { id: 'categories' as const, label: $translate('adminCrud.categories') },
    { id: 'subcategories' as const, label: $translate('adminCrud.subcategories') },
    { id: 'badges' as const, label: $translate('adminCrud.badgeDefinitions') },
    { id: 'attempts' as const, label: $translate('adminCrud.allAttempts') },
  ]);
</script>

<svelte:head>
  <title>Admin Dashboard — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="mb-6 flex items-center justify-between">
    <h1 class="text-2xl font-bold tracking-[-0.03em]">{$translate('admin.title')}</h1>
    <button class="btn-pill btn-pill-ghost btn-pill-sm" onclick={loadData}>Refresh</button>
  </div>

  <!-- Tabs -->
  <div class="mb-6 flex gap-1 border-b border-[var(--color-surface-200-800)]">
    {#each tabs as tab}
      <button
        class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px
          {activeTab === tab.id
            ? 'border-[var(--color-primary-500)] text-[var(--color-primary-500)]'
            : 'border-transparent hover:border-[var(--color-surface-300-700)]'}"
        onclick={() => activeTab = tab.id}
      >
        {tab.label}
      </button>
    {/each}
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <div class="text-sm opacity-50">{$translate('general.loading')}</div>
    </div>
  {:else if error}
    <div class="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-500">
      {error}
    </div>
  {:else}
    <!-- Overview Tab -->
    {#if activeTab === 'overview'}
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div class="frame-lift p-5">
          <p class="text-xs uppercase tracking-wider opacity-50">{$translate('admin.totalUsers')}</p>
          <p class="mt-1 text-3xl font-bold">{stats?.total_users ?? 0}</p>
        </div>
        <div class="frame-lift p-5">
          <p class="text-xs uppercase tracking-wider opacity-50">{$translate('admin.totalQuizzes')}</p>
          <p class="mt-1 text-3xl font-bold">{stats?.total_quizzes ?? 0}</p>
        </div>
        <div class="frame-lift p-5">
          <p class="text-xs uppercase tracking-wider opacity-50">{$translate('admin.totalAttempts')}</p>
          <p class="mt-1 text-3xl font-bold">{stats?.total_attempts ?? 0}</p>
        </div>
        <div class="frame-lift p-5">
          <p class="text-xs uppercase tracking-wider opacity-50">{$translate('admin.dailyActiveUsers')}</p>
          <p class="mt-1 text-3xl font-bold">{stats?.daily_active_users ?? 0}</p>
        </div>
        <div class="frame-lift p-5">
          <p class="text-xs uppercase tracking-wider opacity-50">{$translate('admin.weeklyActiveUsers')}</p>
          <p class="mt-1 text-3xl font-bold">{stats?.weekly_active_users ?? 0}</p>
        </div>
      </div>

    <!-- Users Tab -->
    {:else if activeTab === 'users'}
      <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.username')}</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.email')}</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.role')}</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.created')}</th>
              <th class="px-4 py-3 text-right font-medium">{$translate('admin.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {#each users as user}
              <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                <td class="px-4 py-3 font-medium">{user.username}</td>
                <td class="px-4 py-3 opacity-70">{user.email}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium
                    {user.role === 'admin'
                      ? 'bg-purple-500/10 text-purple-500'
                      : 'bg-blue-500/10 text-blue-500'}">
                    {user.role}
                  </span>
                </td>
                <td class="px-4 py-3 opacity-50">{new Date(user.created_at).toLocaleDateString()}</td>
                <td class="px-4 py-3 text-right">
                  {#if user.role === 'admin'}
                    <button
                      class="btn-pill btn-pill-ghost btn-pill-xs"
                      onclick={() => changeRole(user.id, 'user')}
                    >
                      {$translate('admin.demoteUser')}
                    </button>
                  {:else}
                    <button
                      class="btn-pill btn-pill-ghost btn-pill-xs"
                      onclick={() => changeRole(user.id, 'admin')}
                    >
                      {$translate('admin.promoteAdmin')}
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      {#if usersTotalPages > 1}
        <div class="mt-4 flex items-center justify-between">
          <p class="text-xs opacity-50">{$translate('general.page')} {usersPage} {$translate('general.of')} {usersTotalPages}</p>
          <div class="flex gap-2">
            <button
              class="btn-pill btn-pill-ghost btn-pill-sm"
              disabled={usersPage <= 1}
              onclick={() => { usersPage--; loadUsers(); }}
            >
              {$translate('quiz.previous')}
            </button>
            <button
              class="btn-pill btn-pill-ghost btn-pill-sm"
              disabled={usersPage >= usersTotalPages}
              onclick={() => { usersPage++; loadUsers(); }}
            >
              {$translate('quiz.next')}
            </button>
          </div>
        </div>
      {/if}

    <!-- Top Quizzes Tab -->
    {:else if activeTab === 'quizzes'}
      <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
              <th class="px-4 py-3 text-left font-medium">#</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.quizTitle')}</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.creator')}</th>
              <th class="px-4 py-3 text-right font-medium">{$translate('admin.attempts')}</th>
            </tr>
          </thead>
          <tbody>
            {#each topQuizzes as quiz, i}
              <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                <td class="px-4 py-3 opacity-50">{i + 1}</td>
                <td class="px-4 py-3 font-medium">
                  <a href="/quizzes/{quiz.id}" class="hover:text-[var(--color-primary-500)]">{quiz.title}</a>
                </td>
                <td class="px-4 py-3 opacity-70">{quiz.creator_username}</td>
                <td class="px-4 py-3 text-right font-mono">{quiz.attempt_count}</td>
              </tr>
            {/each}
            {#if topQuizzes.length === 0}
              <tr><td colspan="4" class="px-4 py-8 text-center opacity-50">{$translate('general.noData')}</td></tr>
            {/if}
          </tbody>
        </table>
      </div>

    <!-- Top Creators Tab -->
    {:else if activeTab === 'creators'}
      <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
              <th class="px-4 py-3 text-left font-medium">#</th>
              <th class="px-4 py-3 text-left font-medium">{$translate('admin.creator')}</th>
              <th class="px-4 py-3 text-right font-medium">{$translate('dashboard.quizzesCreated')}</th>
              <th class="px-4 py-3 text-right font-medium">{$translate('admin.attempts')}</th>
              <th class="px-4 py-3 text-right font-medium">{$translate('dashboard.totalXp')}</th>
            </tr>
          </thead>
          <tbody>
            {#each topCreators as creator, i}
              <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                <td class="px-4 py-3 opacity-50">{i + 1}</td>
                <td class="px-4 py-3 font-medium">{creator.username}</td>
                <td class="px-4 py-3 text-right font-mono">{creator.quiz_count}</td>
                <td class="px-4 py-3 text-right font-mono">{creator.total_attempts}</td>
                <td class="px-4 py-3 text-right font-mono">{creator.xp}</td>
              </tr>
            {/each}
            {#if topCreators.length === 0}
              <tr><td colspan="5" class="px-4 py-8 text-center opacity-50">{$translate('general.noData')}</td></tr>
            {/if}
          </tbody>
        </table>
      </div>

    <!-- Categories Tab -->
    {:else if activeTab === 'categories'}
      <div class="space-y-4">
        <div class="frame p-4">
          <h3 class="mb-3 text-sm font-semibold">{catEditing ? $translate('adminCrud.editCategory') : $translate('adminCrud.newCategory')}</h3>
          <div class="flex gap-2">
            <input
              bind:value={catFormName}
              placeholder={$translate('adminCrud.name')}
              class="flex-1 rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]"
            />
            <button onclick={saveCategory} disabled={catSubmitting || !catFormName.trim()} class="btn-pill btn-pill-primary btn-pill-sm">
              {catSubmitting ? $translate('adminCrud.saving') : (catEditing ? $translate('adminCrud.update') : $translate('adminCrud.create'))}
            </button>
            {#if catEditing}
              <button onclick={() => { catEditing = null; catFormName = ''; }} class="btn-pill btn-pill-ghost btn-pill-sm">{$translate('adminCrud.cancel')}</button>
            {/if}
          </div>
          {#if catError}<p class="mt-1 text-xs text-red-500">{catError}</p>{/if}
        </div>
        <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.name')}</th>
                <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {#each categories as cat}
                <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                  <td class="px-4 py-3">{cat.name}</td>
                  <td class="px-4 py-3 text-right">
                    <button onclick={() => editCategory(cat)} class="btn-pill btn-pill-ghost btn-pill-xs mr-1">{$translate('adminCrud.edit')}</button>
                    <button onclick={() => confirmDeleteCategory(cat)} class="btn-pill btn-pill-ghost btn-pill-xs text-red-500">{$translate('adminCrud.delete')}</button>
                  </td>
                </tr>
              {/each}
              {#if categories.length === 0}
                <tr><td colspan="2" class="px-4 py-8 text-center opacity-50">{$translate('adminCrud.noItems')}</td></tr>
              {/if}
            </tbody>
          </table>
        </div>
      </div>

    <!-- Subcategories Tab -->
    {:else if activeTab === 'subcategories'}
      <div class="space-y-4">
        <div class="frame p-4">
          <h3 class="mb-3 text-sm font-semibold">{subEditing ? $translate('adminCrud.editSubcategory') : $translate('adminCrud.newSubcategory')}</h3>
          <div class="flex flex-wrap gap-2">
            <select
              bind:value={subFormCategoryId}
              class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]"
            >
              <option value="">{$translate('adminCrud.parentCategory')}...</option>
              {#each categories as cat}
                <option value={cat.id}>{cat.name}</option>
              {/each}
            </select>
            <input
              bind:value={subFormName}
              placeholder={$translate('adminCrud.name')}
              class="flex-1 rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]"
            />
            <button onclick={saveSubcategory} disabled={subSubmitting || !subFormName.trim() || !subFormCategoryId} class="btn-pill btn-pill-primary btn-pill-sm">
              {subSubmitting ? $translate('adminCrud.saving') : (subEditing ? $translate('adminCrud.update') : $translate('adminCrud.create'))}
            </button>
            {#if subEditing}
              <button onclick={() => { subEditing = null; subFormName = ''; subFormCategoryId = ''; }} class="btn-pill btn-pill-ghost btn-pill-sm">{$translate('adminCrud.cancel')}</button>
            {/if}
          </div>
          {#if subError}<p class="mt-1 text-xs text-red-500">{subError}</p>{/if}
        </div>
        <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.name')}</th>
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.category')}</th>
                <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {#each subcategories as sub}
                <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                  <td class="px-4 py-3">{sub.name}</td>
                  <td class="px-4 py-3 opacity-70">{(categories.find(c => c.id === sub.category_id)?.name || sub.category_id)}</td>
                  <td class="px-4 py-3 text-right">
                    <button onclick={() => editSubcategory(sub)} class="btn-pill btn-pill-ghost btn-pill-xs mr-1">{$translate('adminCrud.edit')}</button>
                    <button onclick={() => confirmDeleteSubcategory(sub)} class="btn-pill btn-pill-ghost btn-pill-xs text-red-500">{$translate('adminCrud.delete')}</button>
                  </td>
                </tr>
              {/each}
              {#if subcategories.length === 0}
                <tr><td colspan="3" class="px-4 py-8 text-center opacity-50">{$translate('adminCrud.noItems')}</td></tr>
              {/if}
            </tbody>
          </table>
        </div>
      </div>

    <!-- Badges Tab -->
    {:else if activeTab === 'badges'}
      <div class="space-y-4">
        <div class="frame p-4">
          <h3 class="mb-3 text-sm font-semibold">{badgeEditing ? $translate('adminCrud.editBadge') : $translate('adminCrud.newBadgeDefinition')}</h3>
          <div class="grid gap-3 sm:grid-cols-2">
            <input bind:value={badgeFormKey} placeholder="Key" class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]" />
            <input bind:value={badgeFormName} placeholder={$translate('adminCrud.name')} class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]" />
            <input bind:value={badgeFormDesc} placeholder={$translate('adminCrud.description')} class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]" />
            <input bind:value={badgeFormIcon} placeholder={$translate('adminCrud.icon')} class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)]" />
          </div>
          <textarea
            bind:value={badgeFormCriteria}
            placeholder="Criteria (JSON)"
            class="mt-2 w-full rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none focus:border-[var(--color-primary-500)] font-mono"
            rows="3"
          ></textarea>
          {#if badgeError}<p class="mt-1 text-xs text-red-500">{badgeError}</p>{/if}
          <div class="mt-3 flex gap-2">
            <button onclick={saveBadge} disabled={badgeSubmitting || !badgeFormKey.trim() || !badgeFormName.trim()} class="btn-pill btn-pill-primary btn-pill-sm">
              {badgeSubmitting ? $translate('adminCrud.saving') : (badgeEditing ? $translate('adminCrud.update') : $translate('adminCrud.create'))}
            </button>
            {#if badgeEditing}
              <button onclick={() => { badgeEditing = null; badgeFormKey = ''; badgeFormName = ''; badgeFormDesc = ''; badgeFormIcon = ''; badgeFormCriteria = ''; }} class="btn-pill btn-pill-ghost btn-pill-sm">{$translate('adminCrud.cancel')}</button>
            {/if}
          </div>
        </div>
        <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.key')}</th>
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.name')}</th>
                <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.icon')}</th>
                <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {#each badgeDefs as b}
                <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                  <td class="px-4 py-3 font-mono text-xs">{b.key}</td>
                  <td class="px-4 py-3">{b.name}</td>
                  <td class="px-4 py-3">{b.icon}</td>
                  <td class="px-4 py-3 text-right">
                    <button onclick={() => editBadge(b)} class="btn-pill btn-pill-ghost btn-pill-xs mr-1">{$translate('adminCrud.edit')}</button>
                    <button onclick={() => confirmDeleteBadge(b)} class="btn-pill btn-pill-ghost btn-pill-xs text-red-500">{$translate('adminCrud.delete')}</button>
                  </td>
                </tr>
              {/each}
              {#if badgeDefs.length === 0}
                <tr><td colspan="4" class="px-4 py-8 text-center opacity-50">{$translate('adminCrud.noItems')}</td></tr>
              {/if}
            </tbody>
          </table>
        </div>
      </div>

    <!-- Attempts Tab -->
    {:else if activeTab === 'attempts'}
      <div>
        {#if allAttempts.length > 0}
          <div class="overflow-x-auto rounded-xl border border-[var(--color-surface-200-800)]">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]">
                  <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.user')}</th>
                  <th class="px-4 py-3 text-left font-medium">{$translate('adminCrud.quiz')}</th>
                  <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.score')}</th>
                  <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.total')}</th>
                  <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.timeSpent')}</th>
                  <th class="px-4 py-3 text-right font-medium">{$translate('adminCrud.createdAt')}</th>
                </tr>
              </thead>
              <tbody>
                {#each allAttempts as att}
                  <tr class="border-b border-[var(--color-surface-200-800)] last:border-0 hover:bg-[var(--color-surface-100-900)]/50">
                    <td class="px-4 py-3">{att.username}</td>
                    <td class="px-4 py-3 max-w-[200px] truncate">{att.quiz_title}</td>
                    <td class="px-4 py-3 text-right font-mono">{att.score}</td>
                    <td class="px-4 py-3 text-right font-mono">{att.total}</td>
                    <td class="px-4 py-3 text-right font-mono">{att.time_spent}s</td>
                    <td class="px-4 py-3 text-right text-xs opacity-50">{new Date(att.created_at).toLocaleDateString()}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          {#if attemptsTotalPages > 1}
            <div class="mt-4 flex items-center justify-between">
              <p class="text-xs opacity-50">{$translate('general.page')} {attemptsPage} {$translate('general.of')} {attemptsTotalPages}</p>
              <div class="flex gap-2">
                <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={attemptsPage <= 1} onclick={() => { attemptsPage--; loadAttempts(); }}>{$translate('quiz.previous')}</button>
                <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={attemptsPage >= attemptsTotalPages} onclick={() => { attemptsPage++; loadAttempts(); }}>{$translate('quiz.next')}</button>
              </div>
            </div>
          {/if}
        {:else}
          <div class="py-10 text-center"><p class="text-sm opacity-50">{$translate('adminCrud.noItems')}</p></div>
        {/if}
      </div>
    {/if}

    <!-- Delete Confirmation Modal -->
    {#if deleteItem}
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div class="frame w-full max-w-sm p-6">
          <h3 class="text-lg font-semibold">{$translate('adminCrud.deleteConfirm', {item: deleteType})}</h3>
          <div class="mt-6 flex justify-end gap-2">
            <button onclick={() => { deleteItem = null; deleteType = ''; }} class="btn-pill btn-pill-ghost btn-pill-sm">{$translate('adminCrud.cancel')}</button>
            <button onclick={confirmDelete} disabled={deleteSubmitting} class="btn-pill btn-pill-primary btn-pill-sm bg-red-500 hover:bg-red-600">
              {deleteSubmitting ? $translate('adminCrud.deleting') : $translate('adminCrud.confirm')}
            </button>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

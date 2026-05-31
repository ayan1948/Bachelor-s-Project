<script>
    import { onMount } from 'svelte';
    import { token } from '../../stores';

    let username = '';
    let email = '';
    let image_file = 'default.jpg';
    let newUsername = '';
    let newEmail = '';
    /**
     * @type {FileList | null}
     */
    let picture = null;
    let message = '';
    let error = '';

    onMount(async () => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            token.set(storedToken);
            try {
                const response = await fetch('http://127.0.0.1:5000/users/me/', {
                    headers: {
                        'Authorization': `Bearer ${storedToken}`
                    }
                });
                if (response.ok) {
                    const user = await response.json();
                    username = user.username;
                    email = user.email;
                    image_file = user.image_file;
                    newUsername = username;
                    newEmail = email;
                }
            } catch (error) {
                console.error("Failed to fetch user data:", error);
            }
        }
    });

    async function updateAccount() {
        const storedToken = localStorage.getItem('token');
        const formData = new FormData();
        if (newUsername !== username) formData.append('username', newUsername);
        if (newEmail !== email) formData.append('email', newEmail);
        if (picture && picture.length > 0) formData.append('picture', picture[0]);

        try {
            const response = await fetch('http://127.0.0.1:5000/users/me/', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${storedToken}`
                },
                body: formData,
            });

            if (response.ok) {
                message = "Account information updated successfully";
                error = '';
                // Refresh data
                const userResponse = await fetch('http://127.0.0.1:5000/users/me/', {
                    headers: {
                        'Authorization': `Bearer ${storedToken}`
                    }
                });
                if (userResponse.ok) {
                    const user = await userResponse.json();
                    username = user.username;
                    email = user.email;
                    image_file = user.image_file;
                }
            } else {
                const errorData = await response.json();
                error = errorData.detail || 'Failed to update account';
                message = '';
            }
        } catch (e) {
            error = 'An error occurred. Please try again.';
            message = '';
        }
    }
</script>

<div class="content-section">
    <div class="media">
        <img class="rounded-circle account-img" src={`http://127.0.0.1:5000/static/profile_pics/${image_file}`} alt="Profile Picture">
        <div class="media-body">
            <h2 class="account-heading">{username}</h2>
            <p class="text-secondary">{email}</p>
        </div>
    </div>
    <form on:submit|preventDefault={updateAccount} enctype="multipart/form-data">
        <fieldset class="form-group">
            <legend class="border-bottom mb-4">Account Info</legend>
            {#if message}
                <div class="alert alert-success">{message}</div>
            {/if}
            {#if error}
                <div class="alert alert-danger">{error}</div>
            {/if}
            <div class="form-group">
                <label class="form-control-label" for="username">Username</label>
                <input type="text" id="username" class="form-control form-control-lg" bind:value={newUsername}>
            </div>
            <div class="form-group">
                <label class="form-control-label" for="email">Email</label>
                <input type="email" id="email" class="form-control form-control-lg" bind:value={newEmail}>
            </div>
            <div class="form-group">
                <label for="picture">Update Profile Picture</label>
                <input type="file" id="picture" class="form-control-file" accept="image/*" bind:files={picture}>
            </div>
        </fieldset>
        <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Update</button>
        </div>
    </form>
</div>
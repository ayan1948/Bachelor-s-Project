<script>
    import { goto } from '$app/navigation';

    let username = '';
    let email = '';
    let password = '';
    let confirm_password = '';
    let error = '';

    async function register() {
        if (password !== confirm_password) {
            error = "Passwords do not match.";
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (response.ok) {
                // Success, maybe show a toast and redirect to login
                goto('/login');
            } else {
                const errorData = await response.json();
                error = errorData.detail || 'Registration failed';
            }
        } catch (e) {
            error = 'An error occurred. Please try again.';
        }
    }
</script>

<div class="content-section">
    <form on:submit|preventDefault={register}>
        <fieldset class="form-group">
            <legend class="border-bottom mb-4">Join Today</legend>
            {#if error}
                <div class="alert alert-danger">{error}</div>
            {/if}
            <div class="form-group">
                <label class="form-control-label" for="username">Username</label>
                <input type="text" id="username" class="form-control form-control-lg" bind:value={username} required>
            </div>
            <div class="form-group">
                <label class="form-control-label" for="email">Email</label>
                <input type="email" id="email" class="form-control form-control-lg" bind:value={email} required>
            </div>
            <div class="form-group">
                <label class="form-control-label" for="password">Password</label>
                <input type="password" id="password" class="form-control form-control-lg" bind:value={password} required>
            </div>
            <div class="form-group">
                <label class="form-control-label" for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" class="form-control form-control-lg" bind:value={confirm_password} required>
            </div>
        </fieldset>
        <div class="form-group">
            <button type="submit" class="btn btn-outline-info">Sign Up</button>
        </div>
    </form>
</div>
<div class="border-top pt-3">
    <small class="text-muted">
        Already Have An Account? <a class="ml-2" href="/login">Sign In</a>
    </small>
</div>
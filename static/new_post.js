function new_post() {
    const publicKey = localStorage.getItem('public_key');
    if (!publicKey) {
        login();
    } else {
        let arr = window.location.toString().split('/');
        const chain = arr[arr.length - 1].split('?')[0];
        const fetchOptions = {
            method: 'POST',
            body: JSON.stringify({
                title: document.getElementById('post_title').value,
                content: document.getElementById('post_content').value,
                public_key: publicKey,
                chain: chain,
            }),
            headers: {'Content-Type': 'application/json'}
        };
        fetch('/api/create_post', fetchOptions)
            .then((response) => response.json())
            .then(() => {
                window.location.reload();
            });
    }
}

module.exports = {
    apps: [
        {
            name: "object_gay",
            script: "./scripts/pm2/run.sh",
            args: "object_gay.app",
            env: {
                PORT: 5100,
            },
            min_uptime: "5s",
            max_restarts: 5,
        },
        {
            name: "get_object_gay",
            script: "./scripts/pm2/run.sh",
            args: "object_gay.subdomains.get",
            env: {
                PORT: 5101,
            },
            min_uptime: "5s",
            max_restarts: 5,
        },
    ]
}

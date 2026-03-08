export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const body = await request.json();
        const { domain, email } = body;

        if (!domain || !email) {
            return new Response(JSON.stringify({ error: "Missing domain or email" }), {
                status: 400,
                headers: { "Content-Type": "application/json" }
            });
        }

        // Logic: Capture the Lead
        // In a production environment, you would save this to:
        // 1. Cloudflare D1 (SQL Database)
        // 2. Cloudflare KV (Key-Value Store)
        // 3. Discord Webhook (Real-time notification)

        console.log(`Lead Captured: Domain=${domain}, Email=${email}`);

        // OPTIONAL: Send to Discord (uncomment and add DISCORD_WEBHOOK_URL to Cloudflare Env)
        /*
        if (env.DISCORD_WEBHOOK_URL) {
            await fetch(env.DISCORD_WEBHOOK_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    content: `🚀 **New SEO Audit Lead Captured!**\n**Domain**: ${domain}\n**Email**: ${email}\n**Framework**: ${request.headers.get("referer") || "Direct"}`
                })
            });
        }
        */

        return new Response(JSON.stringify({
            success: true,
            message: "Audit started. You will receive the report shortly.",
            auditId: `audit-${Math.random().toString(36).substr(2, 9)}`
        }), {
            headers: { "Content-Type": "application/json" }
        });

    } catch (err) {
        return new Response(JSON.stringify({ error: "Invalid request payload" }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }
}

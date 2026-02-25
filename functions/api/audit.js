export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const body = await request.json();
        const { domain, email, framework } = body;

        if (!domain || !email) {
            return new Response(JSON.stringify({ error: "Missing domain or email" }), {
                status: 400,
                headers: { "Content-Type": "application/json" }
            });
        }

        const timestamp = new Date().toISOString();
        const leadId = `lead_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;

        // --- 核心逻辑：持久化存储到 Cloudflare KV ---
        // 需要在 Cloudflare 控制台绑定名为 LEADS_KV 的命名空间
        if (env.LEADS_KV) {
            const leadData = {
                id: leadId,
                domain,
                email,
                framework: framework || "Direct",
                timestamp,
                status: "pending"
            };
            await env.LEADS_KV.put(leadId, JSON.stringify(leadData));
            console.log(`Lead stored in KV: ${leadId}`);
        } else {
            // 调试模式：如果没找到绑定，直接抛错，方便用户在浏览器看到
            const availableKeys = Object.keys(env).join(", ");
            throw new Error(`Critical Error: LEADS_KV binding is missing. Available bindings: [${availableKeys}]. Please check Settings -> Bindings -> KV.`);
        }

        // --- 实时通知：Discord Webhook (可选) ---
        if (env.DISCORD_WEBHOOK_URL) {
            try {
                await fetch(env.DISCORD_WEBHOOK_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        embeds: [{
                            title: "🚀 New SEO Audit Lead!",
                            color: 0x00ffcc,
                            fields: [
                                { name: "Domain", value: domain, inline: true },
                                { name: "Email", value: email, inline: true },
                                { name: "Framework", value: framework || "Matrix", inline: false }
                            ],
                            timestamp: timestamp
                        }]
                    })
                });
            } catch (e) { console.error("Discord notification failed", e); }
        }

        return new Response(JSON.stringify({
            success: true,
            message: "Audit task queued successfully.",
            leadId: leadId
        }), {
            headers: { "Content-Type": "application/json" }
        });

    } catch (err) {
        return new Response(JSON.stringify({ error: "Invalid request payload", details: err.message }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }
}

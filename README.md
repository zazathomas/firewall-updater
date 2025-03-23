# firewall-updater

Ever felt the need to overengineer your network security updates? Well, you're in the right place! This script is my one-stop solution for updating the K8s gateway API policies in a GitHub repository, which is vigilantly watched by ArgoCD for any updates. But wait, there's more! After tweaking the gateway API policy file, it also updates the network security group rules in Oracle Cloud to allow ingress traffic to certain assets. 🚀

## How It Works

1. **Uptime Kuma**: My trusty service monitor, Uptime Kuma, keeps an eye on my local and cloud services. When a service becomes unreachable and triggers a 403 Forbidden error, it sends a webhook notification to n8n for further action.
2. **n8n Workflow Automation**: n8n processes the webhook notification from Uptime Kuma and executes this script using Docker Compose on a dedicated infrastructure node.
3. **ArgoCD**: ArgoCD detects updates in the GitHub repository and applies the changes, enabling ingress traffic from a new public IP address to services running on My Kubernetes cluster.
4. **Oracle Cloud**: Finally, the script updates Oracle Cloud's network security group rules, ensuring specified assets are accessible via the updated ingress traffic configurations.

## Why Use This?

- **Cost Effective**: This approach is subjectively more cost effective than paying 6 euro per month for a static IP from my ISP.
- **Overengineered Fun**: Because why not? Embrace the complexity and enjoy the ride!
- **Automated Updates**: Removes the need for manual updates by seamlessly integrating service monitoring, policy management, and security rule updates.
- **Enhanced Security**: Keeps network security policies up-to-date, reducing risks and ensuring accessibility only to trusted sources.

## Future Improvements
1. Implement push notifications for workflow failures.
2. Modify the workflow to cover other use cases e.g. AWS Security Groups, Cloudflare Tunnels etc.


## Preferred Deployment Method
I've included all the necessary files required to setup a similar workflow in this repository including the n8n workflow file and Dockerfile.
I recommend deploying this setup using Docker, The Docker image is available on my GHCR repository.


Happy automating! 🤖

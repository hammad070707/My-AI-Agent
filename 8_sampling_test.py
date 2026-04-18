from mcp.server.fastmcp import FastMCP,Context
#Context: Ye sab se aham hai! Ye wo "Special Access Card" hai jo hamare tool ko ye ijazat deta hai ke wo Claude ke dimaagh ko call kar sakay.
import logging #Ye "Khufiya Diary" likhne ke liye hai (jo hum ne Day 9 mein parha tha).

mcp=FastMCP("Smart_Brain_Server")
#tool create
@mcp.tool()
#async def: Hum ne def se pehle async lagaya. Kyun? Kyunke AI se jawab mangna 
#aik lamba kaam hai. async computer ko kehta hai: "Bhai, jab tak AI jawab de raha hai, tum baaki kaam karte raho, hang mat hona."

async def analyze_and_format_text(raw_text:str,ctx:Context)->str:
    """Ganda data leta hai aur Claude se usay saaf karwata hai (Sampling)."""
    try: # Hum ne security lagayi taake agar Claude mana kar de (User "Deny" kar de), to code crash na ho.
        # Iska matlab hai: "Ruk jao! Jab tak Claude (LLM) ka jawab nahi aata, agli line par mat jana."
        # ctx.sampling.create_message Ye wo "Telephone Call" hai jo hamara server Claude ko kar raha hai. Hum Claude ko aik Order bhej rahe hain ke: "Bhai, ye data parho aur mujhe saaf kar ke do."
        response=await ctx.request_sampling.create_message(
            messages=[ #messages: Ye bilkul waisa hi hai jaise hum ChatGPT ya Claude ko prompt dete hain. Hum ne server ke andar aik Prompt likh diya.

                {
                    "role": "user", #role: user: Server ab "User" ban kar Claude se sawal puch raha hai.
                    "content": {
                        "type": "text",
                        "text": f"Neeche diye gaye data ko saaf karo: {raw_text}" 
                    }
                }
            ],
            max_tokens=100,
            system_prompt="Tum aik data cleaning expert ho." #system_prompt: Hum ne Claude ko bataya ke jab wo is sawal ka jawab de, to wo "Expert" ban kar soche.
        )
        ai_brain_answer=response.content.text
        return f"server nay AI se mashware kiya , AI nay yeh kaha {ai_brain_answer}"
        #response.content.text: Claude ne jo hoshiyar jawab diya, hum ne usay dabba khol kar nikal liya.
        #return: Hum ne wo jawab wapas user ki chat screen par bhej diya.
    except Exception as e:
        return f"❌ Sampling fail ho gayi: {str(e)}"
if __name__ == "__main__":
    mcp.run(transport="stdio")


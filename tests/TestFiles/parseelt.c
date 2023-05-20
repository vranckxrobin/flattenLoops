#include <string.h>
#include "minixml.h"

static void parseelt(struct xmlparser * p)
{
	int i;
	const char * elementname;
	while(p->xml < (p->xmlend - 1))
	{
		if((p->xml + 4) <= p->xmlend && (0 == memcmp(p->xml, "<!--", 4)))
		{
			p->xml += 3;
			/* ignore comments */
			do
			{
				p->xml++;
				if ((p->xml + 3) >= p->xmlend)
					return;
			}
			while(memcmp(p->xml, "-->", 3) != 0);
			p->xml += 3;
		}
		else if((p->xml)[0]=='<' && (p->xml)[1]!='?')
		{
			i = 0; elementname = ++p->xml;
			while( !IS_WHITE_SPACE(*p->xml)
				  && (*p->xml!='>') && (*p->xml!='/')
				 )
			{
				i++; p->xml++;
				if (p->xml >= p->xmlend)
					return;
				/* to ignore namespace : */
				if(*p->xml==':')
				{
					i = 0;
					elementname = ++p->xml;
				}
			}
			if(i>0)
			{
				if(p->starteltfunc)
					p->starteltfunc(p->data, elementname, i);
				if(parseatt(p))
					return;
				if(*p->xml!='/')
				{
					const char * data;
					i = 0; data = ++p->xml;
					if (p->xml >= p->xmlend)
						return;
					while( IS_WHITE_SPACE(*p->xml) )
					{
						i++; p->xml++;
						if (p->xml >= p->xmlend)
							return;
					}
					/* CDATA are at least 9 + 3 characters long : <![CDATA[ ]]> */
					if((p->xmlend >= (p->xml + (9 + 3))) && (memcmp(p->xml, "<![CDATA[", 9) == 0))
					{
						/* CDATA handling */
						p->xml += 9;
						data = p->xml;
						i = 0;
						while(memcmp(p->xml, "]]>", 3) != 0)
						{
							i++; p->xml++;
							if ((p->xml + 3) >= p->xmlend)
								return;
						}
						if(i>0 && p->datafunc)
							p->datafunc(p->data, data, i);
						while(*p->xml!='<')
						{
							p->xml++;
							if (p->xml >= p->xmlend)
								return;
						}
					}
					else
					{
						while(*p->xml!='<')
						{
							i++; p->xml++;
							if ((p->xml + 1) >= p->xmlend)
								return;
						}
						if(i>0 && p->datafunc && *(p->xml + 1) == '/')
							p->datafunc(p->data, data, i);
					}
				}
			}
			else if(*p->xml == '/')
			{
				i = 0; elementname = ++p->xml;
				if (p->xml >= p->xmlend)
					return;
				while((*p->xml != '>'))
				{
					i++; p->xml++;
					if (p->xml >= p->xmlend)
						return;
				}
				if(p->endeltfunc)
					p->endeltfunc(p->data, elementname, i);
				p->xml++;
			}
		}
		else
		{
			p->xml++;
		}
	}
}
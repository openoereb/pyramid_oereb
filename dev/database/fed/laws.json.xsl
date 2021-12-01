<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ili="http://www.interlis.ch/INTERLIS2.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:output omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>
<xsl:template match="/">
[<xsl:for-each select="ili:TRANSFER/ili:DATASECTION/ili:OeREBKRM_V2_0.Dokumente/ili:OeREBKRM_V2_0.Dokumente.Dokument">
    {
        "id": "<xsl:value-of select="@TID"/>",
        "document_type": "<xsl:value-of select="ili:Typ"/>",
        "extract_index": <xsl:value-of select="number(ili:AuszugIndex)"/>,
        "title": {<xsl:for-each select="ili:Titel/ili:LocalisationCH_V1.MultilingualText/ili:LocalisedText/ili:LocalisationCH_V1.LocalisedText">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "abbreviation": {<xsl:for-each select="ili:Abkuerzung/ili:LocalisationCH_V1.MultilingualText/ili:LocalisedText/ili:LocalisationCH_V1.LocalisedText">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "official_number": {<xsl:for-each select="ili:OffizielleNr/ili:LocalisationCH_V1.MultilingualText/ili:LocalisedText/ili:LocalisationCH_V1.LocalisedText">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "text_at_web": {<xsl:for-each select="ili:TextImWeb/ili:OeREBKRM_V2_0.MultilingualUri/ili:LocalisedText/ili:OeREBKRM_V2_0.LocalisedUri">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "index": "<xsl:value-of select="ili:AuszugIndex"/>",
        "law_status": "<xsl:value-of select="ili:Rechtsstatus"/>",
        "published_from": "<xsl:value-of select="ili:publiziertAb"/>",
        "office_id": "<xsl:value-of select="ili:ZustaendigeStelle/@REF"/>"
    }<xsl:if test="not(position() = last())">,</xsl:if>
</xsl:for-each>
]
</xsl:template>
</xsl:stylesheet>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ili="http://www.interlis.ch/INTERLIS2.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:output omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>
<xsl:template match="/">
[<xsl:for-each select="ili:TRANSFER/ili:DATASECTION/ili:OeREBKRM_V2_0.Dokumente/ili:OeREBKRM_V2_0.Amt.Amt">
    {
        "id": "<xsl:value-of select="@TID"/>",
        "name": {<xsl:for-each select="ili:Name/ili:LocalisationCH_V1.MultilingualText/ili:LocalisedText/ili:LocalisationCH_V1.LocalisedText">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "office_at_web": {<xsl:for-each select="ili:AmtImWeb/ili:OeREBKRM_V2_0.MultilingualUri/ili:LocalisedText/ili:OeREBKRM_V2_0.LocalisedUri">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        },
        "uid": "<xsl:value-of select="ili:UID"/>"
    }<xsl:if test="not(position() = last())">,</xsl:if>
</xsl:for-each>
]
</xsl:template>
</xsl:stylesheet>

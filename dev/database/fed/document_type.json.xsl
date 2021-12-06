<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ili="http://www.interlis.ch/INTERLIS2.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:output omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>
<xsl:template match="/">
[<xsl:for-each select="ili:TRANSFER/ili:DATASECTION/ili:OeREBKRMkvs_V2_0.Konfiguration/ili:OeREBKRMkvs_V2_0.Konfiguration.DokumentTypTxt">
    {
        "code": "<xsl:value-of select="ili:Code"/>",
        "title": {<xsl:for-each select="ili:Titel/ili:LocalisationCH_V1.MultilingualText/ili:LocalisedText/ili:LocalisationCH_V1.LocalisedText">
            "<xsl:value-of select="ili:Language"/>": "<xsl:value-of select="ili:Text"/>"<xsl:if test="not(position() = last())">,</xsl:if>
        </xsl:for-each>
        }
    }<xsl:if test="not(position() = last())">,</xsl:if>
</xsl:for-each>
]
</xsl:template>
</xsl:stylesheet>

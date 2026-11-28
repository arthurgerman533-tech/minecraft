Code
[[

	static const float GLOBE_STAR_GRID   = 4.0f;
	static const float GLOBE_STAR_MARGIN = 0.05f;
	static const float GLOBE_MILKY_WAY   = 0.07f;
	static const float GLOBE_SUN_RADIUS  = 0.008f;
	static const float GLOBE_MOON_RADIUS = 0.017f;
	static const float GLOBE_MOON_ANGLE  = 2.0f;

	float3 GlobeHash3( float3 p )
	{
		p = frac( p * float3( 0.1031f, 0.103f, 0.0973f ) );
		p += dot( p, p.yxz + 33.33f );
		return frac( ( p.xxy + p.yxx ) * p.zyx );
	}

	float GlobeNoise( float3 p )
	{
		float3 i = floor( p );
		float3 u = frac( p );
		u = u * u * ( 3.0f - 2.0f * u );
		float a = GlobeHash3( i ).x;
		float b = GlobeHash3( i + float3( 1.0f, 0.0f, 0.0f ) ).x;
		float c = GlobeHash3( i + float3( 0.0f, 1.0f, 0.0f ) ).x;
		float d = GlobeHash3( i + float3( 1.0f, 1.0f, 0.0f ) ).x;
		float e = GlobeHash3( i + float3( 0.0f, 0.0f, 1.0f ) ).x;
		float f = GlobeHash3( i + float3( 1.0f, 0.0f, 1.0f ) ).x;
		float g = GlobeHash3( i + float3( 0.0f, 1.0f, 1.0f ) ).x;
		float h = GlobeHash3( i + float3( 1.0f, 1.0f, 1.0f ) ).x;
		return lerp( lerp( lerp( a, b, u.x ), lerp( c, d, u.x ), u.y ), lerp( lerp( e, f, u.x ), lerp( g, h, u.x ), u.y ), u.z );
	}

	float GlobeFbm( float3 p )
	{
		float vSum = 0.5f * GlobeNoise( p );
		vSum += 0.25f * GlobeNoise( p * 2.03f + 1.7f );
		vSum += 0.125f * GlobeNoise( p * 4.11f + 3.1f );
		vSum += 0.0625f * GlobeNoise( p * 8.27f + 5.3f );
		return vSum / 0.9375f;
	}

	float3 GlobeCube( float3 vDir )
	{
		float3 vAbs = abs( vDir );
		if ( vAbs.x >= vAbs.y && vAbs.x >= vAbs.z )
			return float3( vDir.x > 0.0f ? 0.0f : 1.0f, vDir.yz / vAbs.x );
		if ( vAbs.y >= vAbs.z )
			return float3( vDir.y > 0.0f ? 2.0f : 3.0f, vDir.xz / vAbs.y );
		return float3( vDir.z > 0.0f ? 4.0f : 5.0f, vDir.xy / vAbs.z );
	}

	float3 GlobeCubeDir( float vFace, float2 vUV )
	{
		float vSide = frac( vFace * 0.5f ) < 0.25f ? 1.0f : -1.0f;
		if ( vFace < 1.5f )
			return normalize( float3( vSide, vUV.x, vUV.y ) );
		if ( vFace < 3.5f )
			return normalize( float3( vUV.x, vSide, vUV.y ) );
		return normalize( float3( vUV.x, vUV.y, vSide ) );
	}

	float2 GlobeStarRegion( float3 vDir )
	{
		float3 vCube = GlobeCube( vDir );
		float2 vCell = clamp( floor( ( vCube.yz * 0.5f + 0.5f ) * GLOBE_STAR_GRID ), 0.0f, GLOBE_STAR_GRID - 1.0f );
		return float2( vCube.x, vCell.y * GLOBE_STAR_GRID + vCell.x );
	}

	float3 GlobeStar( float3 vDir, float vPixel, float3 vStar, float vBright, float3 vTint )
	{
		float vAngle = length( vDir - vStar );
		float vD = vAngle / vPixel;
		float vCore = min( vBright, 1.0f ) * exp( -vD * vD / ( 0.8f + 0.9f * min( vBright, 2.0f ) ) );
		float vB = 1.4f * ( 1.0f - exp( -vBright / 1.4f ) );
		float vGlow = 0.06f * vB * vB * exp( -vD / ( 1.5f + 2.5f * vB ) );
		vGlow *= 1.0f - smoothstep( GLOBE_STAR_MARGIN * 0.6f, GLOBE_STAR_MARGIN, vAngle );
		return vTint * ( vCore + vGlow );
	}

	float3 GlobeStarDim( float3 vDir, float vScale, float3 vStar, float3 vColor, float vFalloff )
	{
		float3 vOff = vDir - vStar;
		return vColor * exp2( -dot( vOff, vOff ) * vScale * vFalloff );
	}

	float3 GlobeFieldStars( float3 vDir, float vPixel, float vCells, float vChance, float vMaxBright, float vSeed )
	{
		float3 vCube = GlobeCube( vDir );
		float2 vCell = floor( ( vCube.yz * 0.5f + 0.5f ) * vCells );
		float3 vRand = GlobeHash3( float3( vCell, vCube.x * 131.0f + vSeed ) );
		if ( vRand.z > vChance )
			return float3( 0.0f, 0.0f, 0.0f );
		float3 vRand2 = GlobeHash3( vRand * 917.0f + vSeed );
		float2 vSpot = ( vCell + 0.25f + 0.5f * vRand.xy ) / vCells * 2.0f - 1.0f;
		float vBright = vMaxBright * ( 0.15f + 0.85f * vRand2.x * vRand2.x * vRand2.x );
		float3 vTint = lerp( float3( 0.78f, 0.85f, 1.0f ), float3( 1.0f, 0.88f, 0.72f ), vRand2.y );
		return GlobeStar( vDir, vPixel, GlobeCubeDir( vCube.x, vSpot ), vBright, vTint );
	}

	static const float3 GLOBE_GALACTIC_POLE = float3( -0.8677f, -0.1981f, 0.456f );
	static const float3 GLOBE_GALACTIC_CENTER = float3( -0.0549f, -0.8734f, -0.4838f );

	float3 GlobeCatalogStars( float3 vDir, float vPixel )
	{
		float2 vRegion = GlobeStarRegion( vDir );
		float vScale = 1.0f / ( vPixel * vPixel );
		float3 vSum = float3( 0.0f, 0.0f, 0.0f );
		if ( vRegion.x < 0.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6775f, -0.4155f, -0.6069f ), float3( 0.257f, 0.285f, 0.348f ), 1.296f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.8373f, -0.2336f, -0.4943f ), 0.889f, float3( 0.845f, 0.897f, 1.0f ) );
			}
			else if ( vRegion.y > 1.5f && vRegion.y < 2.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7347f, 0.0846f, -0.6731f ), float3( 0.477f, 0.4f, 0.309f ), 1.174f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6741f, 0.2736f, -0.6861f ), float3( 0.284f, 0.206f, 0.138f ), 1.366f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8035f, -0.5266f, -0.2778f ), float3( 0.353f, 0.358f, 0.374f ), 1.269f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7937f, -0.6005f, -0.0971f ), float3( 0.366f, 0.331f, 0.28f ), 1.277f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8784f, -0.478f, -0.0056f ), float3( 0.357f, 0.309f, 0.246f ), 1.286f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8784f, -0.478f, -0.0056f ), float3( 0.357f, 0.309f, 0.246f ), 1.286f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.9233f, -0.2706f, -0.2726f ), float3( 0.252f, 0.27f, 0.305f ), 1.342f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.934f, 0.1798f, -0.3088f ), 0.569f, float3( 1.0f, 0.855f, 0.673f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.9405f, 0.2902f, -0.1768f ), float3( 0.279f, 0.229f, 0.173f ), 1.373f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8641f, 0.4218f, -0.2746f ), float3( 0.272f, 0.253f, 0.223f ), 1.381f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8197f, 0.5705f, -0.0519f ), float3( 0.343f, 0.26f, 0.181f ), 1.301f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8641f, 0.4218f, -0.2746f ), float3( 0.272f, 0.253f, 0.223f ), 1.381f );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8172f, -0.5502f, 0.1715f ), float3( 0.477f, 0.35f, 0.236f ), 1.174f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8784f, -0.478f, -0.0056f ), float3( 0.357f, 0.309f, 0.246f ), 1.286f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8559f, -0.2143f, 0.4707f ), float3( 0.47f, 0.332f, 0.219f ), 1.18f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.9371f, -0.2303f, 0.2623f ), float3( 0.353f, 0.387f, 0.453f ), 1.194f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8784f, -0.478f, -0.0056f ), float3( 0.357f, 0.309f, 0.246f ), 1.286f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.9251f, -0.33f, 0.1879f ), float3( 0.215f, 0.238f, 0.286f ), 1.365f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8671f, -0.2734f, 0.4163f ), float3( 0.274f, 0.241f, 0.196f ), 1.378f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.8733f, 0.032f, 0.4862f ), 0.564f, float3( 0.743f, 0.823f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8202f, 0.4483f, 0.3552f ), float3( 0.363f, 0.382f, 0.42f ), 1.225f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.9635f, 0.0557f, 0.2619f ), float3( 0.26f, 0.294f, 0.382f ), 1.262f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.7797f, 0.4833f, 0.3981f ), 0.581f, float3( 1.0f, 0.824f, 0.626f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6983f, 0.7123f, 0.0713f ), float3( 0.444f, 0.316f, 0.21f ), 1.203f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8202f, 0.4483f, 0.3552f ), float3( 0.363f, 0.382f, 0.42f ), 1.225f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7555f, 0.6527f, 0.0564f ), float3( 0.233f, 0.247f, 0.276f ), 1.376f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5501f, -0.6206f, 0.5588f ), float3( 0.46f, 0.392f, 0.308f ), 1.188f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6445f, -0.5755f, 0.5034f ), float3( 0.316f, 0.273f, 0.217f ), 1.33f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.8733f, 0.032f, 0.4862f ), 0.564f, float3( 0.743f, 0.823f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8559f, -0.2143f, 0.4707f ), float3( 0.47f, 0.332f, 0.219f ), 1.18f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8158f, -0.2849f, 0.5033f ), float3( 0.361f, 0.323f, 0.271f ), 1.283f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8671f, -0.2734f, 0.4163f ), float3( 0.274f, 0.241f, 0.196f ), 1.378f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.7756f, 0.2435f, 0.5824f ), 0.564f, float3( 1.0f, 0.724f, 0.484f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.8733f, 0.032f, 0.4862f ), 0.564f, float3( 0.743f, 0.823f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8458f, 0.1466f, 0.513f ), float3( 0.305f, 0.242f, 0.177f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7659f, 0.4119f, 0.4936f ), float3( 0.279f, 0.273f, 0.263f ), 1.366f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.7797f, 0.4833f, 0.3981f ), 0.581f, float3( 1.0f, 0.824f, 0.626f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.6339f, 0.3805f, 0.6734f ), 0.509f, float3( 1.0f, 0.771f, 0.547f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.8202f, 0.4483f, 0.3552f ), float3( 0.363f, 0.382f, 0.42f ), 1.225f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6918f, 0.4388f, 0.5734f ), float3( 0.305f, 0.319f, 0.35f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7659f, 0.4119f, 0.4936f ), float3( 0.279f, 0.273f, 0.263f ), 1.366f );
			}
		}
		else if ( vRegion.x < 1.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.6853f, -0.4228f, -0.593f ), 0.564f, float3( 1.0f, 0.858f, 0.676f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6548f, -0.3395f, -0.6753f ), float3( 0.244f, 0.273f, 0.343f ), 1.301f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7611f, -0.4681f, -0.449f ), float3( 0.305f, 0.254f, 0.194f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6279f, -0.6506f, -0.4271f ), float3( 0.302f, 0.212f, 0.139f ), 1.346f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6631f, -0.3434f, -0.6651f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7526f, -0.2761f, -0.5978f ), float3( 0.326f, 0.35f, 0.397f ), 1.246f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8654f, -0.3104f, -0.3935f ), float3( 0.35f, 0.308f, 0.252f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6548f, -0.3395f, -0.6753f ), float3( 0.244f, 0.273f, 0.343f ), 1.301f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6631f, -0.3434f, -0.6651f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7061f, -0.652f, -0.2763f ), float3( 0.348f, 0.364f, 0.397f ), 1.246f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.9141f, -0.3564f, -0.1936f ), 0.974f, float3( 0.682f, 0.771f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9512f, -0.0657f, -0.3014f ), float3( 0.32f, 0.355f, 0.431f ), 1.215f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9075f, -0.1372f, -0.3971f ), float3( 0.418f, 0.371f, 0.307f ), 1.227f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9506f, -0.1246f, -0.2843f ), float3( 0.278f, 0.305f, 0.359f ), 1.285f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9222f, -0.0408f, -0.3846f ), float3( 0.35f, 0.273f, 0.196f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8654f, -0.3104f, -0.3935f ), float3( 0.35f, 0.308f, 0.252f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9158f, -0.4015f, -0.0104f ), float3( 0.248f, 0.262f, 0.29f ), 1.36f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9222f, -0.0408f, -0.3846f ), float3( 0.35f, 0.273f, 0.196f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9154f, 0.2903f, -0.2789f ), float3( 0.331f, 0.265f, 0.195f ), 1.314f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.7779f, 0.61f, -0.1505f ), 0.587f, float3( 1.0f, 0.754f, 0.522f ) );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.7838f, -0.527f, 0.3286f ), 1.633f, float3( 1.0f, 0.805f, 0.597f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8325f, -0.4553f, 0.3156f ), float3( 0.41f, 0.395f, 0.366f ), 1.233f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.9667f, 0.0462f, 0.2516f ), 0.541f, float3( 0.845f, 0.897f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8325f, -0.4553f, 0.3156f ), float3( 0.41f, 0.395f, 0.366f ), 1.233f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9459f, -0.2631f, 0.1901f ), float3( 0.382f, 0.334f, 0.271f ), 1.262f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9158f, -0.4015f, -0.0104f ), float3( 0.248f, 0.262f, 0.29f ), 1.36f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.969f, -0.2398f, 0.0593f ), float3( 0.289f, 0.209f, 0.14f ), 1.361f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.8645f, 0.4579f, 0.2074f ), 0.807f, float3( 0.743f, 0.823f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.9667f, 0.0462f, 0.2516f ), 0.541f, float3( 0.845f, 0.897f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9178f, 0.1863f, 0.3506f ), float3( 0.376f, 0.396f, 0.437f ), 1.209f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8525f, 0.3976f, 0.3394f ), float3( 0.427f, 0.351f, 0.267f ), 1.219f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.9448f, 0.1912f, 0.2661f ), float3( 0.234f, 0.255f, 0.295f ), 1.354f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.826f, 0.3998f, 0.3974f ), float3( 0.267f, 0.269f, 0.279f ), 1.371f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.8645f, 0.4579f, 0.2074f ), 0.807f, float3( 0.743f, 0.823f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8525f, 0.3976f, 0.3394f ), float3( 0.427f, 0.351f, 0.267f ), 1.219f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7628f, 0.5056f, 0.4031f ), float3( 0.354f, 0.322f, 0.276f ), 1.29f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.689f, 0.7173f, 0.1036f ), float3( 0.331f, 0.285f, 0.225f ), 1.314f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.826f, 0.3998f, 0.3974f ), float3( 0.267f, 0.269f, 0.279f ), 1.371f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6695f, -0.5871f, 0.4551f ), float3( 0.407f, 0.354f, 0.283f ), 1.237f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6182f, -0.4833f, 0.6199f ), float3( 0.309f, 0.32f, 0.345f ), 1.299f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7612f, -0.1899f, 0.62f ), float3( 0.272f, 0.301f, 0.368f ), 1.275f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6961f, 0.1554f, 0.7009f ), float3( 0.348f, 0.288f, 0.219f ), 1.296f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.682f, 0.3096f, 0.6626f ), float3( 0.341f, 0.246f, 0.165f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.826f, 0.3998f, 0.3974f ), float3( 0.267f, 0.269f, 0.279f ), 1.371f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6598f, 0.3179f, 0.6809f ), float3( 0.227f, 0.245f, 0.279f ), 1.373f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.8241f, 0.151f, 0.546f ), float3( 0.274f, 0.21f, 0.147f ), 1.378f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7628f, 0.5056f, 0.4031f ), float3( 0.354f, 0.322f, 0.276f ), 1.29f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.682f, 0.3096f, 0.6626f ), float3( 0.341f, 0.246f, 0.165f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6346f, 0.5275f, 0.5649f ), float3( 0.328f, 0.239f, 0.161f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.826f, 0.3998f, 0.3974f ), float3( 0.267f, 0.269f, 0.279f ), 1.371f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6598f, 0.3179f, 0.6809f ), float3( 0.227f, 0.245f, 0.279f ), 1.373f );
			}
		}
		else if ( vRegion.x < 2.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3933f, 0.6573f, -0.6428f ), 0.512f, float3( 0.666f, 0.759f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4814f, 0.7738f, -0.4116f ), float3( 0.374f, 0.37f, 0.365f ), 1.258f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4165f, 0.8061f, -0.4204f ), float3( 0.295f, 0.236f, 0.175f ), 1.354f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.2214f, 0.8464f, -0.4844f ), 0.748f, float3( 0.692f, 0.78f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2634f, 0.8562f, -0.4445f ), 0.63f, float3( 1.0f, 0.94f, 0.84f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3128f, 0.814f, -0.4894f ), float3( 0.351f, 0.387f, 0.463f ), 1.186f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2634f, 0.7529f, -0.6032f ), float3( 0.407f, 0.292f, 0.194f ), 1.237f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2484f, 0.8804f, -0.4041f ), float3( 0.263f, 0.29f, 0.347f ), 1.298f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0766f, 0.8621f, -0.501f ), float3( 0.243f, 0.273f, 0.347f ), 1.298f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.032f, 0.8108f, -0.5845f ), float3( 0.329f, 0.271f, 0.205f ), 1.316f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1196f, 0.7191f, -0.6845f ), float3( 0.239f, 0.264f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2762f, 0.6733f, -0.6858f ), float3( 0.308f, 0.228f, 0.154f ), 1.339f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4165f, 0.8061f, -0.4204f ), float3( 0.295f, 0.236f, 0.175f ), 1.354f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2351f, 0.8516f, -0.4685f ), float3( 0.276f, 0.191f, 0.125f ), 1.376f );
			}
			else if ( vRegion.y > 1.5f && vRegion.y < 2.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0735f, 0.825f, -0.5603f ), float3( 0.31f, 0.344f, 0.42f ), 1.225f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.032f, 0.8108f, -0.5845f ), float3( 0.329f, 0.271f, 0.205f ), 1.316f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4814f, 0.7738f, -0.4116f ), float3( 0.374f, 0.37f, 0.365f ), 1.258f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4165f, 0.8061f, -0.4204f ), float3( 0.295f, 0.236f, 0.175f ), 1.354f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.1875f, 0.9392f, -0.2876f ), 3.352f, float3( 0.8f, 0.87f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2634f, 0.8562f, -0.4445f ), 0.63f, float3( 1.0f, 0.94f, 0.84f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.0941f, 0.9466f, -0.3083f ), 0.587f, float3( 0.682f, 0.771f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2484f, 0.8804f, -0.4041f ), float3( 0.263f, 0.29f, 0.347f ), 1.298f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4165f, 0.8061f, -0.4204f ), float3( 0.295f, 0.236f, 0.175f ), 1.354f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2351f, 0.8516f, -0.4685f ), float3( 0.276f, 0.191f, 0.125f ), 1.376f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.1951f, 0.9704f, -0.1427f ), 1.506f, float3( 0.785f, 0.857f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1036f, 0.9944f, -0.021f ), 0.676f, float3( 0.702f, 0.789f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0838f, 0.9959f, -0.0339f ), 0.566f, float3( 0.692f, 0.78f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0526f, 0.9844f, -0.168f ), 0.564f, float3( 0.713f, 0.797f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1218f, 0.9925f, -0.0052f ), 0.517f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.113f, 0.9453f, -0.3061f ), float3( 0.392f, 0.404f, 0.433f ), 1.213f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1064f, 0.989f, -0.103f ), float3( 0.266f, 0.302f, 0.393f ), 1.25f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2247f, 0.9704f, -0.0887f ), float3( 0.337f, 0.354f, 0.389f ), 1.254f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1291f, 0.9261f, -0.3544f ), float3( 0.38f, 0.344f, 0.292f ), 1.264f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.218f, 0.8987f, -0.3806f ), float3( 0.318f, 0.238f, 0.164f ), 1.328f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1958f, 0.9401f, -0.2791f ), float3( 0.222f, 0.246f, 0.299f ), 1.349f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1542f, 0.9871f, -0.0418f ), float3( 0.208f, 0.233f, 0.292f ), 1.358f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4934f, 0.8379f, -0.2336f ), float3( 0.359f, 0.259f, 0.173f ), 1.285f );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4181f, 0.9038f, 0.0911f ), 1.32f, float3( 0.97f, 0.96f, 0.952f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.689f, 0.7173f, 0.1036f ), float3( 0.331f, 0.285f, 0.225f ), 1.314f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.661f, 0.742f, 0.1118f ), float3( 0.289f, 0.271f, 0.243f ), 1.361f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4181f, 0.9038f, 0.0911f ), 1.32f, float3( 0.97f, 0.96f, 0.952f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0209f, 0.9914f, 0.1289f ), 1.242f, float3( 1.0f, 0.67f, 0.43f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.1571f, 0.9464f, 0.2823f ), 0.602f, float3( 0.8f, 0.87f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0924f, 0.9192f, 0.3829f ), float3( 0.372f, 0.265f, 0.176f ), 1.271f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3673f, 0.9189f, 0.1442f ), float3( 0.278f, 0.306f, 0.368f ), 1.275f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1725f, 0.8888f, 0.4247f ), float3( 0.354f, 0.27f, 0.19f ), 1.29f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0599f, 0.9219f, 0.3828f ), float3( 0.304f, 0.219f, 0.146f ), 1.344f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1914f, 0.9558f, 0.2232f ), float3( 0.283f, 0.28f, 0.277f ), 1.358f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0209f, 0.9914f, 0.1289f ), 1.242f, float3( 1.0f, 0.67f, 0.43f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.3439f, 0.895f, 0.2842f ), 1.04f, float3( 1.0f, 0.732f, 0.492f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1506f, 0.9824f, 0.1106f ), 0.697f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1287f, 0.8684f, 0.4788f ), 0.694f, float3( 0.733f, 0.814f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1036f, 0.9944f, -0.021f ), 0.676f, float3( 0.702f, 0.789f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0838f, 0.9959f, -0.0339f ), 0.566f, float3( 0.692f, 0.78f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1218f, 0.9925f, -0.0052f ), 0.517f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0908f, 0.9283f, 0.3607f ), float3( 0.246f, 0.276f, 0.35f ), 1.294f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2991f, 0.9465f, 0.1212f ), float3( 0.31f, 0.305f, 0.299f ), 1.328f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1542f, 0.9871f, -0.0418f ), float3( 0.208f, 0.233f, 0.292f ), 1.358f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3733f, 0.8865f, 0.2735f ), float3( 0.254f, 0.264f, 0.286f ), 1.365f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6983f, 0.7123f, 0.0713f ), float3( 0.444f, 0.316f, 0.21f ), 1.203f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4989f, 0.7644f, 0.4084f ), float3( 0.282f, 0.311f, 0.374f ), 1.269f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4857f, 0.847f, 0.2163f ), float3( 0.204f, 0.226f, 0.276f ), 1.376f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3915f, 0.7912f, 0.4699f ), 0.898f, float3( 1.0f, 0.86f, 0.68f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3406f, 0.7778f, 0.5283f ), 0.587f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3406f, 0.7778f, 0.5283f ), float3( 0.305f, 0.328f, 0.372f ), 1.271f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3915f, 0.7912f, 0.4699f ), 0.898f, float3( 1.0f, 0.86f, 0.68f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0015f, 0.7078f, 0.7065f ), 0.611f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3406f, 0.7778f, 0.5283f ), 0.587f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.001f, 0.7964f, 0.6048f ), float3( 0.322f, 0.355f, 0.424f ), 1.221f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3406f, 0.7778f, 0.5283f ), float3( 0.305f, 0.328f, 0.372f ), 1.271f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1725f, 0.8888f, 0.4247f ), float3( 0.354f, 0.27f, 0.19f ), 1.29f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.1305f, 0.6823f, 0.7193f ), 1.536f, float3( 1.0f, 0.91f, 0.78f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.1287f, 0.8684f, 0.4788f ), 0.694f, float3( 0.733f, 0.814f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0015f, 0.7078f, 0.7065f ), 0.611f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.001f, 0.7964f, 0.6048f ), float3( 0.322f, 0.355f, 0.424f ), 1.221f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2272f, 0.8057f, 0.5471f ), float3( 0.41f, 0.301f, 0.202f ), 1.235f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1807f, 0.6985f, 0.6924f ), float3( 0.348f, 0.338f, 0.318f ), 1.292f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1739f, 0.7316f, 0.6591f ), float3( 0.227f, 0.255f, 0.321f ), 1.325f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4432f, 0.7243f, 0.5282f ), float3( 0.325f, 0.342f, 0.378f ), 1.266f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4989f, 0.7644f, 0.4084f ), float3( 0.282f, 0.311f, 0.374f ), 1.269f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3892f, 0.6597f, 0.6429f ), float3( 0.262f, 0.293f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5382f, 0.5631f, 0.6272f ), float3( 0.287f, 0.204f, 0.135f ), 1.363f );
			}
		}
		else if ( vRegion.x < 3.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4604f, -0.8001f, -0.3846f ), float3( 0.365f, 0.404f, 0.494f ), 1.159f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4448f, -0.6074f, -0.6583f ), float3( 0.273f, 0.307f, 0.391f ), 1.252f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4529f, -0.7754f, -0.4402f ), float3( 0.26f, 0.292f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3769f, -0.8194f, -0.432f ), float3( 0.32f, 0.336f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4842f, -0.5841f, -0.6514f ), float3( 0.215f, 0.243f, 0.313f ), 1.334f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6279f, -0.6506f, -0.4271f ), float3( 0.302f, 0.212f, 0.139f ), 1.346f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3915f, -0.6789f, -0.6211f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3448f, -0.8264f, -0.4451f ), 0.984f, float3( 1.0f, 0.674f, 0.434f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.0916f, -0.7923f, -0.6033f ), 0.701f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.0723f, -0.7278f, -0.682f ), 0.62f, float3( 0.967f, 0.96f, 0.96f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2479f, -0.7881f, -0.5634f ), 0.502f, float3( 1.0f, 0.824f, 0.626f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0593f, -0.7745f, -0.6297f ), float3( 0.324f, 0.366f, 0.472f ), 1.178f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1012f, -0.7891f, -0.6059f ), float3( 0.281f, 0.318f, 0.41f ), 1.235f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3162f, -0.8225f, -0.4728f ), float3( 0.257f, 0.293f, 0.383f ), 1.26f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3769f, -0.8194f, -0.432f ), float3( 0.32f, 0.336f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0219f, -0.862f, -0.5064f ), float3( 0.352f, 0.303f, 0.239f ), 1.292f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0414f, -0.7635f, -0.6445f ), float3( 0.34f, 0.331f, 0.316f ), 1.299f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2307f, -0.753f, -0.6163f ), float3( 0.234f, 0.264f, 0.336f ), 1.309f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0353f, -0.7974f, -0.6024f ), float3( 0.315f, 0.258f, 0.195f ), 1.332f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1495f, -0.8939f, -0.4226f ), float3( 0.21f, 0.237f, 0.305f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.151f, -0.7127f, -0.685f ), float3( 0.287f, 0.284f, 0.283f ), 1.353f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3915f, -0.6789f, -0.6211f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 1.5f && vRegion.y < 2.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0869f, -0.8207f, -0.5647f ), 0.627f, float3( 0.785f, 0.857f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.2141f, -0.8706f, -0.443f ), 0.575f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2339f, -0.8349f, -0.4982f ), float3( 0.36f, 0.383f, 0.429f ), 1.217f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0794f, -0.8639f, -0.4974f ), float3( 0.407f, 0.313f, 0.221f ), 1.237f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.11f, -0.8965f, -0.4293f ), float3( 0.385f, 0.328f, 0.257f ), 1.258f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0219f, -0.862f, -0.5064f ), float3( 0.352f, 0.303f, 0.239f ), 1.292f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0414f, -0.7635f, -0.6445f ), float3( 0.34f, 0.331f, 0.316f ), 1.299f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0616f, -0.7988f, -0.5985f ), float3( 0.331f, 0.241f, 0.162f ), 1.314f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1763f, -0.8735f, -0.4538f ), float3( 0.239f, 0.264f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0353f, -0.7974f, -0.6024f ), float3( 0.315f, 0.258f, 0.195f ), 1.332f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.255f, -0.8481f, -0.4644f ), float3( 0.298f, 0.242f, 0.182f ), 1.351f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4604f, -0.8001f, -0.3846f ), float3( 0.365f, 0.404f, 0.494f ), 1.159f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.644f, -0.7474f, -0.163f ), float3( 0.317f, 0.351f, 0.427f ), 1.219f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.451f, -0.8257f, -0.3388f ), float3( 0.324f, 0.356f, 0.424f ), 1.221f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4439f, -0.8937f, -0.0644f ), float3( 0.399f, 0.289f, 0.193f ), 1.244f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.7061f, -0.652f, -0.2763f ), float3( 0.348f, 0.364f, 0.397f ), 1.246f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4529f, -0.7754f, -0.4402f ), float3( 0.26f, 0.292f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3769f, -0.8194f, -0.432f ), float3( 0.32f, 0.336f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4278f, -0.9002f, -0.0818f ), float3( 0.31f, 0.27f, 0.217f ), 1.337f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3448f, -0.8264f, -0.4451f ), 0.984f, float3( 1.0f, 0.674f, 0.434f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2068f, -0.9401f, -0.271f ), float3( 0.388f, 0.415f, 0.467f ), 1.182f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3476f, -0.9195f, -0.1834f ), float3( 0.354f, 0.383f, 0.437f ), 1.209f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.451f, -0.8257f, -0.3388f ), float3( 0.324f, 0.356f, 0.424f ), 1.221f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4439f, -0.8937f, -0.0644f ), float3( 0.399f, 0.289f, 0.193f ), 1.244f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3769f, -0.8194f, -0.432f ), float3( 0.32f, 0.336f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4278f, -0.9002f, -0.0818f ), float3( 0.31f, 0.27f, 0.217f ), 1.337f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1495f, -0.8939f, -0.4226f ), float3( 0.21f, 0.237f, 0.305f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0042f, -0.9855f, -0.1698f ), float3( 0.295f, 0.254f, 0.202f ), 1.354f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.2141f, -0.8706f, -0.443f ), 0.575f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.11f, -0.8965f, -0.4293f ), float3( 0.385f, 0.328f, 0.257f ), 1.258f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2798f, -0.8905f, -0.3588f ), float3( 0.355f, 0.355f, 0.363f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1763f, -0.8735f, -0.4538f ), float3( 0.239f, 0.264f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.0927f, -0.9944f, -0.0506f ), float3( 0.307f, 0.268f, 0.218f ), 1.341f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.255f, -0.8481f, -0.4644f ), float3( 0.298f, 0.242f, 0.182f ), 1.351f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0042f, -0.9855f, -0.1698f ), float3( 0.295f, 0.254f, 0.202f ), 1.354f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.284f, -0.955f, -0.0851f ), float3( 0.211f, 0.233f, 0.28f ), 1.371f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5581f, -0.7896f, -0.2551f ), float3( 0.336f, 0.307f, 0.264f ), 1.309f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.542f, -0.8402f, -0.0143f ), float3( 0.238f, 0.262f, 0.312f ), 1.335f );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4514f, -0.7779f, 0.4371f ), 0.581f, float3( 0.85f, 0.9f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5547f, -0.8245f, 0.1119f ), float3( 0.418f, 0.342f, 0.259f ), 1.227f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.1065f, -0.9702f, 0.2175f ), 0.558f, float3( 0.875f, 0.915f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3553f, -0.86f, 0.3663f ), float3( 0.393f, 0.344f, 0.279f ), 1.25f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0718f, -0.9942f, 0.0796f ), float3( 0.393f, 0.323f, 0.245f ), 1.25f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1769f, -0.8901f, 0.4201f ), float3( 0.274f, 0.292f, 0.326f ), 1.319f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.265f, -0.9504f, 0.1629f ), float3( 0.316f, 0.261f, 0.198f ), 1.33f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0523f, -0.8837f, 0.4652f ), float3( 0.283f, 0.261f, 0.228f ), 1.368f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1904f, -0.9497f, 0.2485f ), float3( 0.274f, 0.207f, 0.143f ), 1.378f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.4592f, -0.8748f, 0.1542f ), 1.083f, float3( 0.91f, 0.936f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4396f, -0.8791f, 0.1842f ), float3( 0.403f, 0.297f, 0.2f ), 1.24f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2733f, -0.9316f, 0.2396f ), float3( 0.283f, 0.307f, 0.352f ), 1.292f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3639f, -0.9298f, 0.0543f ), float3( 0.278f, 0.28f, 0.289f ), 1.358f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.4592f, -0.8748f, 0.1542f ), 1.083f, float3( 0.91f, 0.936f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4396f, -0.8791f, 0.1842f ), float3( 0.403f, 0.297f, 0.2f ), 1.24f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.542f, -0.8402f, -0.0143f ), float3( 0.238f, 0.262f, 0.312f ), 1.335f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4669f, -0.8189f, 0.3337f ), float3( 0.276f, 0.2f, 0.134f ), 1.376f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4514f, -0.7779f, 0.4371f ), 0.581f, float3( 0.85f, 0.9f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.5292f, -0.7196f, 0.4495f ), 0.517f, float3( 0.79f, 0.861f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5496f, -0.6295f, 0.5492f ), float3( 0.276f, 0.241f, 0.194f ), 1.376f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2868f, -0.802f, 0.524f ), float3( 0.385f, 0.365f, 0.33f ), 1.258f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1769f, -0.8901f, 0.4201f ), float3( 0.274f, 0.292f, 0.326f ), 1.319f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.156f, -0.7853f, 0.5992f ), float3( 0.323f, 0.244f, 0.168f ), 1.323f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0523f, -0.8837f, 0.4652f ), float3( 0.283f, 0.261f, 0.228f ), 1.368f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.1251f, -0.7694f, 0.6264f ), 1.576f, float3( 0.8f, 0.87f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3406f, -0.815f, 0.4689f ), float3( 0.336f, 0.279f, 0.213f ), 1.309f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2141f, -0.8139f, 0.5401f ), float3( 0.24f, 0.263f, 0.31f ), 1.337f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1811f, -0.8153f, 0.5499f ), float3( 0.223f, 0.242f, 0.279f ), 1.373f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.4438f, -0.6209f, 0.6462f ), 0.525f, float3( 1.0f, 0.94f, 0.84f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5501f, -0.6206f, 0.5588f ), float3( 0.46f, 0.392f, 0.308f ), 1.188f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6445f, -0.5755f, 0.5034f ), float3( 0.316f, 0.273f, 0.217f ), 1.33f );
			}
		}
		else if ( vRegion.x < 4.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6182f, -0.4833f, 0.6199f ), float3( 0.309f, 0.32f, 0.345f ), 1.299f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.534f, -0.5431f, 0.648f ), float3( 0.272f, 0.236f, 0.189f ), 1.381f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.0092f, -0.6226f, 0.7825f ), 0.517f, float3( 1.0f, 0.736f, 0.496f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.194f, -0.4357f, 0.8789f ), float3( 0.399f, 0.352f, 0.29f ), 1.244f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0787f, -0.6064f, 0.7912f ), float3( 0.389f, 0.337f, 0.269f ), 1.254f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0911f, -0.4011f, 0.9115f ), float3( 0.237f, 0.263f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3228f, -0.402f, 0.8569f ), float3( 0.302f, 0.248f, 0.188f ), 1.346f );
			}
			else if ( vRegion.y > 1.5f && vRegion.y < 2.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.0092f, -0.6226f, 0.7825f ), 0.517f, float3( 1.0f, 0.736f, 0.496f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.312f, -0.6328f, 0.7087f ), float3( 0.293f, 0.32f, 0.374f ), 1.269f );
			}
			else if ( vRegion.y > 2.5f && vRegion.y < 3.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.4556f, -0.5362f, 0.7106f ), 0.849f, float3( 0.845f, 0.897f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.4438f, -0.6209f, 0.6462f ), 0.525f, float3( 1.0f, 0.94f, 0.84f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5501f, -0.6206f, 0.5588f ), float3( 0.46f, 0.392f, 0.308f ), 1.188f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.312f, -0.6328f, 0.7087f ), float3( 0.293f, 0.32f, 0.374f ), 1.269f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.5443f, -0.1307f, 0.8286f ), 0.653f, float3( 0.79f, 0.861f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.5815f, -0.2948f, 0.7583f ), 0.624f, float3( 0.702f, 0.789f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.5365f, -0.2058f, 0.8184f ), 0.507f, float3( 0.81f, 0.876f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5919f, 0.0159f, 0.8059f ), float3( 0.372f, 0.404f, 0.465f ), 1.184f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5429f, -0.0366f, 0.839f ), float3( 0.251f, 0.267f, 0.299f ), 1.349f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0101f, 0.0079f, 0.9999f ), 0.575f, float3( 1.0f, 0.96f, 0.88f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2007f, -0.1851f, 0.962f ), 0.558f, float3( 1.0f, 0.747f, 0.511f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.194f, -0.4357f, 0.8789f ), float3( 0.399f, 0.352f, 0.29f ), 1.244f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1996f, -0.2395f, 0.9502f ), float3( 0.282f, 0.302f, 0.341f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0911f, -0.4011f, 0.9115f ), float3( 0.237f, 0.263f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3228f, -0.402f, 0.8569f ), float3( 0.302f, 0.248f, 0.188f ), 1.346f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0101f, 0.0079f, 0.9999f ), 0.575f, float3( 1.0f, 0.96f, 0.88f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3509f, -0.2981f, 0.8877f ), float3( 0.423f, 0.435f, 0.465f ), 1.184f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1183f, -0.3612f, 0.925f ), float3( 0.338f, 0.291f, 0.23f ), 1.307f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2133f, -0.0193f, 0.9768f ), float3( 0.315f, 0.268f, 0.211f ), 1.332f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2628f, -0.2041f, 0.943f ), float3( 0.214f, 0.242f, 0.312f ), 1.335f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4683f, -0.2416f, 0.8499f ), float3( 0.293f, 0.213f, 0.142f ), 1.356f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3116f, -0.3544f, 0.8816f ), float3( 0.282f, 0.248f, 0.203f ), 1.37f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.5124f, 0.0205f, 0.8585f ), 0.507f, float3( 0.957f, 0.96f, 0.984f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4683f, -0.2416f, 0.8499f ), float3( 0.293f, 0.213f, 0.142f ), 1.356f );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4591f, 0.115f, 0.8809f ), 0.646f, float3( 1.0f, 0.843f, 0.655f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5359f, 0.139f, 0.8328f ), float3( 0.38f, 0.415f, 0.482f ), 1.17f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5919f, 0.0159f, 0.8059f ), float3( 0.372f, 0.404f, 0.465f ), 1.184f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6961f, 0.1554f, 0.7009f ), float3( 0.348f, 0.288f, 0.219f ), 1.296f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.682f, 0.3096f, 0.6626f ), float3( 0.341f, 0.246f, 0.165f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4966f, 0.3713f, 0.7845f ), float3( 0.314f, 0.308f, 0.301f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5429f, -0.0366f, 0.839f ), float3( 0.251f, 0.267f, 0.299f ), 1.349f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6598f, 0.3179f, 0.6809f ), float3( 0.227f, 0.245f, 0.279f ), 1.373f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4591f, 0.115f, 0.8809f ), 0.646f, float3( 1.0f, 0.843f, 0.655f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0101f, 0.0079f, 0.9999f ), 0.575f, float3( 1.0f, 0.96f, 0.88f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2982f, 0.3877f, 0.8722f ), float3( 0.292f, 0.263f, 0.222f ), 1.358f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0101f, 0.0079f, 0.9999f ), 0.575f, float3( 1.0f, 0.96f, 0.88f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4742f, 0.1198f, 0.8722f ), float3( 0.331f, 0.369f, 0.458f ), 1.19f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.462f, 0.1816f, 0.8681f ), float3( 0.356f, 0.374f, 0.412f ), 1.233f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4116f, 0.4292f, 0.8039f ), float3( 0.363f, 0.339f, 0.301f ), 1.281f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2133f, -0.0193f, 0.9768f ), float3( 0.315f, 0.268f, 0.211f ), 1.332f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3894f, 0.2123f, 0.8963f ), float3( 0.209f, 0.233f, 0.289f ), 1.361f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.5428f, 0.097f, 0.8342f ), 0.517f, float3( 1.0f, 0.819f, 0.619f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.6339f, 0.3805f, 0.6734f ), 0.509f, float3( 1.0f, 0.771f, 0.547f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.5124f, 0.0205f, 0.8585f ), 0.507f, float3( 0.957f, 0.96f, 0.984f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4742f, 0.1198f, 0.8722f ), float3( 0.331f, 0.369f, 0.458f ), 1.19f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.462f, 0.1816f, 0.8681f ), float3( 0.356f, 0.374f, 0.412f ), 1.233f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4116f, 0.4292f, 0.8039f ), float3( 0.363f, 0.339f, 0.301f ), 1.281f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5205f, 0.1132f, 0.8463f ), float3( 0.279f, 0.269f, 0.25f ), 1.371f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.682f, 0.3096f, 0.6626f ), float3( 0.341f, 0.246f, 0.165f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6346f, 0.5275f, 0.5649f ), float3( 0.328f, 0.239f, 0.161f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4711f, 0.4744f, 0.7436f ), float3( 0.292f, 0.302f, 0.326f ), 1.319f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4966f, 0.3713f, 0.7845f ), float3( 0.314f, 0.308f, 0.301f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6598f, 0.3179f, 0.6809f ), float3( 0.227f, 0.245f, 0.279f ), 1.373f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.0015f, 0.7078f, 0.7065f ), 0.611f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2982f, 0.3877f, 0.8722f ), float3( 0.292f, 0.263f, 0.222f ), 1.358f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.1305f, 0.6823f, 0.7193f ), 1.536f, float3( 1.0f, 0.91f, 0.78f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.405f, 0.5016f, 0.7645f ), 0.646f, float3( 0.98f, 0.96f, 0.928f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.0015f, 0.7078f, 0.7065f ), 0.611f, float3( 0.815f, 0.879f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4116f, 0.4292f, 0.8039f ), float3( 0.363f, 0.339f, 0.301f ), 1.281f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1807f, 0.6985f, 0.6924f ), float3( 0.348f, 0.338f, 0.318f ), 1.292f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3783f, 0.5552f, 0.7407f ), float3( 0.255f, 0.284f, 0.348f ), 1.296f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.405f, 0.5016f, 0.7645f ), 0.646f, float3( 0.98f, 0.96f, 0.928f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.5147f, 0.5527f, 0.6555f ), 0.547f, float3( 0.774f, 0.849f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.6339f, 0.3805f, 0.6734f ), 0.509f, float3( 1.0f, 0.771f, 0.547f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3892f, 0.6597f, 0.6429f ), float3( 0.262f, 0.293f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4116f, 0.4292f, 0.8039f ), float3( 0.363f, 0.339f, 0.301f ), 1.281f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.3783f, 0.5552f, 0.7407f ), float3( 0.255f, 0.284f, 0.348f ), 1.296f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5382f, 0.5631f, 0.6272f ), float3( 0.287f, 0.204f, 0.135f ), 1.363f );
			}
		}
		else if ( vRegion.x < 5.5f )
		{
			if ( vRegion.y > -0.5f && vRegion.y < 0.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5149f, -0.4395f, -0.736f ), float3( 0.348f, 0.391f, 0.499f ), 1.155f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5771f, -0.4653f, -0.6712f ), float3( 0.349f, 0.392f, 0.497f ), 1.157f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5939f, -0.3277f, -0.7348f ), float3( 0.302f, 0.341f, 0.44f ), 1.207f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5193f, -0.5127f, -0.6837f ), float3( 0.283f, 0.319f, 0.412f ), 1.233f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4448f, -0.6074f, -0.6583f ), float3( 0.273f, 0.307f, 0.391f ), 1.252f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6548f, -0.3395f, -0.6753f ), float3( 0.244f, 0.273f, 0.343f ), 1.301f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5265f, -0.5227f, -0.6705f ), float3( 0.228f, 0.257f, 0.328f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4842f, -0.5841f, -0.6514f ), float3( 0.215f, 0.243f, 0.313f ), 1.334f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4506f, -0.5499f, -0.7033f ), float3( 0.205f, 0.23f, 0.29f ), 1.36f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6631f, -0.3434f, -0.6651f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4105f, -0.457f, -0.7891f ), float3( 0.284f, 0.25f, 0.205f ), 1.366f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3915f, -0.6789f, -0.6211f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 0.5f && vRegion.y < 1.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.0723f, -0.7278f, -0.682f ), 0.62f, float3( 0.967f, 0.96f, 0.96f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0854f, -0.5595f, -0.8244f ), float3( 0.378f, 0.283f, 0.194f ), 1.266f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.079f, -0.6396f, -0.7647f ), float3( 0.256f, 0.286f, 0.359f ), 1.285f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.148f, -0.5394f, -0.8289f ), float3( 0.328f, 0.236f, 0.157f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.151f, -0.7127f, -0.685f ), float3( 0.287f, 0.284f, 0.283f ), 1.353f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0833f, -0.5474f, -0.8327f ), float3( 0.216f, 0.24f, 0.295f ), 1.354f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4105f, -0.457f, -0.7891f ), float3( 0.284f, 0.25f, 0.205f ), 1.366f );
			}
			else if ( vRegion.y > 1.5f && vRegion.y < 2.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.3256f, -0.4414f, -0.8361f ), 0.599f, float3( 0.697f, 0.784f, 1.0f ) );
			}
			else if ( vRegion.y > 2.5f && vRegion.y < 3.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.6029f, -0.3198f, -0.7309f ), 0.663f, float3( 0.733f, 0.814f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4304f, -0.5242f, -0.7348f ), float3( 0.331f, 0.285f, 0.225f ), 1.314f );
			}
			else if ( vRegion.y > 3.5f && vRegion.y < 4.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.4239f, -0.2543f, -0.8693f ), 1.175f, float3( 0.682f, 0.771f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4938f, -0.1043f, -0.8633f ), 0.849f, float3( 0.682f, 0.771f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4494f, -0.0524f, -0.8918f ), 0.816f, float3( 0.677f, 0.767f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.538f, -0.0736f, -0.8397f ), 0.701f, float3( 1.0f, 0.722f, 0.482f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4494f, -0.0524f, -0.8918f ), 0.666f, float3( 0.666f, 0.759f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.6458f, -0.1183f, -0.7542f ), 0.533f, float3( 0.795f, 0.866f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5396f, -0.2513f, -0.8035f ), float3( 0.343f, 0.387f, 0.499f ), 1.155f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5939f, -0.3277f, -0.7348f ), float3( 0.302f, 0.341f, 0.44f ), 1.207f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6327f, -0.0231f, -0.7741f ), float3( 0.316f, 0.351f, 0.429f ), 1.217f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5177f, -0.0343f, -0.8549f ), float3( 0.264f, 0.299f, 0.387f ), 1.256f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6548f, -0.3395f, -0.6753f ), float3( 0.244f, 0.273f, 0.343f ), 1.301f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4512f, 0.0479f, -0.8912f ), float3( 0.255f, 0.28f, 0.328f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6631f, -0.3434f, -0.6651f ), float3( 0.195f, 0.221f, 0.284f ), 1.366f );
			}
			else if ( vRegion.y > 4.5f && vRegion.y < 5.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3739f, -0.3126f, -0.8732f ), 1.608f, float3( 1.0f, 0.932f, 0.825f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4239f, -0.2543f, -0.8693f ), 1.175f, float3( 0.682f, 0.771f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4494f, -0.0524f, -0.8918f ), 0.816f, float3( 0.677f, 0.767f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3739f, -0.3126f, -0.8732f ), 0.816f, float3( 1.0f, 0.89f, 0.74f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.4494f, -0.0524f, -0.8918f ), 0.666f, float3( 0.666f, 0.759f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.1096f, -0.3407f, -0.9338f ), 0.605f, float3( 1.0f, 0.754f, 0.522f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3515f, -0.0575f, -0.9344f ), float3( 0.286f, 0.321f, 0.41f ), 1.235f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2318f, -0.3825f, -0.8944f ), float3( 0.357f, 0.361f, 0.378f ), 1.266f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.235f, -0.2774f, -0.9316f ), float3( 0.296f, 0.322f, 0.37f ), 1.273f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3653f, -0.0748f, -0.9279f ), float3( 0.241f, 0.271f, 0.341f ), 1.303f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4512f, 0.0479f, -0.8912f ), float3( 0.255f, 0.28f, 0.328f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3211f, -0.2754f, -0.9061f ), float3( 0.292f, 0.299f, 0.318f ), 1.328f );
			}
			else if ( vRegion.y > 5.5f && vRegion.y < 6.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.3256f, -0.4414f, -0.8361f ), 0.599f, float3( 0.697f, 0.784f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2192f, 0.0247f, -0.9754f ), float3( 0.387f, 0.37f, 0.337f ), 1.256f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4482f, -0.2126f, -0.8683f ), float3( 0.376f, 0.288f, 0.203f ), 1.268f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.266f, -0.3034f, -0.915f ), float3( 0.249f, 0.26f, 0.283f ), 1.368f );
			}
			else if ( vRegion.y > 6.5f && vRegion.y < 7.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.6029f, -0.3198f, -0.7309f ), 0.663f, float3( 0.733f, 0.814f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( 0.6449f, -0.2263f, -0.73f ), 0.552f, float3( 1.0f, 0.72f, 0.48f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4482f, -0.2126f, -0.8683f ), float3( 0.376f, 0.288f, 0.203f ), 1.268f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5949f, -0.1917f, -0.7806f ), float3( 0.229f, 0.244f, 0.273f ), 1.38f );
			}
			else if ( vRegion.y > 7.5f && vRegion.y < 8.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.3804f, 0.4349f, -0.8162f ), 0.593f, float3( 0.82f, 0.882f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3872f, 0.3334f, -0.8596f ), 0.512f, float3( 0.89f, 0.924f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4426f, 0.3645f, -0.8193f ), float3( 0.319f, 0.358f, 0.451f ), 1.196f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6327f, -0.0231f, -0.7741f ), float3( 0.316f, 0.351f, 0.429f ), 1.217f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.6176f, 0.2043f, -0.7595f ), float3( 0.41f, 0.362f, 0.299f ), 1.235f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.408f, 0.1426f, -0.9018f ), float3( 0.272f, 0.307f, 0.395f ), 1.248f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.5177f, -0.0343f, -0.8549f ), float3( 0.264f, 0.299f, 0.387f ), 1.256f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4512f, 0.0479f, -0.8912f ), float3( 0.255f, 0.28f, 0.328f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4335f, 0.3289f, -0.839f ), float3( 0.328f, 0.239f, 0.161f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4398f, 0.1776f, -0.8804f ), float3( 0.224f, 0.247f, 0.298f ), 1.351f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4322f, 0.2083f, -0.8774f ), float3( 0.286f, 0.209f, 0.141f ), 1.365f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3816f, 0.3467f, -0.8569f ), float3( 0.197f, 0.221f, 0.28f ), 1.371f );
			}
			else if ( vRegion.y > 8.5f && vRegion.y < 9.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.2588f, 0.2306f, -0.938f ), 0.683f, float3( 0.8f, 0.87f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2956f, 0.4124f, -0.8617f ), 0.624f, float3( 1.0f, 0.793f, 0.579f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3804f, 0.4349f, -0.8162f ), 0.593f, float3( 0.82f, 0.882f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3872f, 0.3334f, -0.8596f ), 0.512f, float3( 0.89f, 0.924f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4426f, 0.3645f, -0.8193f ), float3( 0.319f, 0.358f, 0.451f ), 1.196f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.408f, 0.1426f, -0.9018f ), float3( 0.272f, 0.307f, 0.395f ), 1.248f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3526f, 0.2309f, -0.9068f ), float3( 0.327f, 0.332f, 0.348f ), 1.296f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4512f, 0.0479f, -0.8912f ), float3( 0.255f, 0.28f, 0.328f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4335f, 0.3289f, -0.839f ), float3( 0.328f, 0.239f, 0.161f ), 1.318f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0982f, 0.46f, -0.8825f ), float3( 0.276f, 0.285f, 0.305f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4398f, 0.1776f, -0.8804f ), float3( 0.224f, 0.247f, 0.298f ), 1.351f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3054f, 0.1527f, -0.9399f ), float3( 0.226f, 0.249f, 0.298f ), 1.351f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4322f, 0.2083f, -0.8774f ), float3( 0.286f, 0.209f, 0.141f ), 1.365f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.3816f, 0.3467f, -0.8569f ), float3( 0.197f, 0.221f, 0.28f ), 1.371f );
			}
			else if ( vRegion.y > 9.5f && vRegion.y < 10.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2192f, 0.0247f, -0.9754f ), float3( 0.387f, 0.37f, 0.337f ), 1.256f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4136f, 0.2358f, -0.8794f ), float3( 0.353f, 0.358f, 0.376f ), 1.268f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.1487f, 0.2273f, -0.9624f ), float3( 0.31f, 0.222f, 0.148f ), 1.337f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2054f, 0.414f, -0.8868f ), float3( 0.293f, 0.259f, 0.213f ), 1.356f );
			}
			else if ( vRegion.y > 10.5f && vRegion.y < 11.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( 0.4927f, 0.2238f, -0.8409f ), 1.267f, float3( 0.718f, 0.801f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.7347f, 0.0846f, -0.6731f ), float3( 0.477f, 0.4f, 0.309f ), 1.174f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.4136f, 0.2358f, -0.8794f ), float3( 0.353f, 0.358f, 0.376f ), 1.268f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6573f, 0.195f, -0.728f ), float3( 0.299f, 0.266f, 0.22f ), 1.349f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.6741f, 0.2736f, -0.6861f ), float3( 0.284f, 0.206f, 0.138f ), 1.366f );
			}
			else if ( vRegion.y > 11.5f && vRegion.y < 12.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.363f, 0.5723f, -0.7353f ), 0.649f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3804f, 0.4349f, -0.8162f ), 0.593f, float3( 0.82f, 0.882f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.5311f, 0.4953f, -0.6875f ), 0.522f, float3( 1.0f, 0.708f, 0.468f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3933f, 0.6573f, -0.6428f ), 0.512f, float3( 0.666f, 0.759f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.4426f, 0.3645f, -0.8193f ), float3( 0.319f, 0.358f, 0.451f ), 1.196f );
			}
			else if ( vRegion.y > 12.5f && vRegion.y < 13.5f )
			{
				vSum += GlobeStar( vDir, vPixel, float3( -0.0632f, 0.6027f, -0.7954f ), 2.304f, float3( 0.875f, 0.915f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.363f, 0.5723f, -0.7353f ), 0.649f, float3( 0.687f, 0.776f, 1.0f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.2956f, 0.4124f, -0.8617f ), 0.624f, float3( 1.0f, 0.793f, 0.579f ) );
				vSum += GlobeStar( vDir, vPixel, float3( -0.3804f, 0.4349f, -0.8162f ), 0.593f, float3( 0.82f, 0.882f, 1.0f ) );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1372f, 0.6195f, -0.7729f ), float3( 0.363f, 0.294f, 0.221f ), 1.281f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.1196f, 0.7191f, -0.6845f ), float3( 0.239f, 0.264f, 0.321f ), 1.325f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2762f, 0.6733f, -0.6858f ), float3( 0.308f, 0.228f, 0.154f ), 1.339f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.0982f, 0.46f, -0.8825f ), float3( 0.276f, 0.285f, 0.305f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( -0.2937f, 0.5256f, -0.7984f ), float3( 0.195f, 0.219f, 0.276f ), 1.376f );
			}
			else if ( vRegion.y > 13.5f && vRegion.y < 14.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.21f, 0.5331f, -0.8196f ), float3( 0.229f, 0.253f, 0.305f ), 1.342f );
				vSum += GlobeStarDim( vDir, vScale, float3( 0.2054f, 0.414f, -0.8868f ), float3( 0.293f, 0.259f, 0.213f ), 1.356f );
			}
			else if ( vRegion.y > 14.5f && vRegion.y < 15.5f )
			{
				vSum += GlobeStarDim( vDir, vScale, float3( 0.5433f, 0.5351f, -0.6469f ), float3( 0.27f, 0.283f, 0.31f ), 1.337f );
			}
		}
		return vSum;
	}

	float3 GlobeMilkyWay( float3 vDir, float vLat )
	{
		float3 vPlane = normalize( vDir - GLOBE_GALACTIC_POLE * vLat + float3( 0.00001f, 0.0f, 0.0f ) );
		float vCore = pow( saturate( 0.5f + 0.5f * dot( vPlane, GLOBE_GALACTIC_CENTER ) ), 4.0f );
		float vWidth = 0.12f + 0.1f * vCore;
		float vClouds = GlobeFbm( vDir * 4.0f );
		float vDetail = GlobeFbm( vDir * 13.0f + 5.3f );
		float vGlow = exp( -vLat * vLat / ( vWidth * vWidth ) ) * ( 0.3f + 0.7f * vCore );
		vGlow *= saturate( 1.6f * vClouds - 0.15f ) * ( 0.7f + 0.6f * vDetail );
		float vLane = ( vLat + 0.03f * ( vDetail - 0.5f ) ) / ( 0.025f + 0.03f * vCore );
		vGlow *= 1.0f - 0.7f * exp( -vLane * vLane ) * smoothstep( 0.2f, 0.6f, vCore + 0.4f * vClouds );
		float3 vTint = lerp( float3( 0.62f, 0.68f, 0.92f ), float3( 1.0f, 0.84f, 0.64f ), vCore );
		return vTint * vGlow * GLOBE_MILKY_WAY;
	}

	float3 GlobeSpace( float3 vDir, float vPixel )
	{
		float vLat = dot( vDir, GLOBE_GALACTIC_POLE );
		float vBand = exp( -vLat * vLat / 0.05f );
		float3 vSum = GlobeMilkyWay( vDir, vLat );
		vSum += GlobeFieldStars( vDir, vPixel, 64.0f, 0.3f + 0.35f * vBand, 0.17f, 0.0f );
		vSum += GlobeFieldStars( vDir, vPixel, 150.0f, 0.18f + 0.45f * vBand, 0.07f, 7.0f );
		vSum += GlobeCatalogStars( vDir, vPixel );
		return vSum;
	}

	float3 GlobeMoonPlanet( float3 vSun )
	{
		float vCos = cos( GLOBE_MOON_ANGLE );
		float vSin = sin( GLOBE_MOON_ANGLE );
		return normalize( float3( vSun.x * vCos - vSun.y * vSin, vSun.x * vSin + vSun.y * vCos, vSun.z + 0.09f ) );
	}

	float3 GlobeSunAndMoon( float3 vDir, float3 vSpace, float vPixel, float3 vSun )
	{
		float3 vMoon = GlobeMoonPlanet( vSun );
		if ( length( vDir - vMoon ) < GLOBE_MOON_RADIUS + 3.0f * vPixel )
		{
			float3 vRight = normalize( cross( vMoon, float3( 0.0f, 0.0f, 1.0f ) ) );
			float3 vTop = cross( vRight, vMoon );
			float2 vUV = float2( dot( vDir - vMoon, vRight ), dot( vDir - vMoon, vTop ) ) / GLOBE_MOON_RADIUS;
			float vR = length( vUV );
			float vEdge = vPixel / GLOBE_MOON_RADIUS;
			float vCover = 1.0f - smoothstep( 1.0f - vEdge, 1.0f + vEdge, vR );
			float vDepth = sqrt( saturate( 1.0f - vR * vR ) );
			float3 vNormal = vUV.x * vRight + vUV.y * vTop - vMoon * vDepth;
			float3 vFace = float3( vUV, vDepth );
			float vMaria = smoothstep( 0.48f, 0.62f, GlobeFbm( vFace * 2.3f + 11.0f ) );
			float vAlbedo = lerp( 0.6f, 0.33f, vMaria ) * ( 0.8f + 0.4f * GlobeFbm( vFace * 11.0f + 3.0f ) );
			float vLit = smoothstep( -0.03f, 0.25f, dot( vNormal, vSun ) );
			vSpace = lerp( vSpace, float3( 0.97f, 0.95f, 0.91f ) * vAlbedo * ( vLit + 0.035f ), vCover );
		}
		float vSunAngle = length( vDir - vSun );
		float vSunDisc = 1.0f - smoothstep( GLOBE_SUN_RADIUS - vPixel, GLOBE_SUN_RADIUS + vPixel, vSunAngle );
		float vCorona = 0.55f * exp( -vSunAngle / 0.02f ) + 0.08f * exp( -vSunAngle / 0.14f );
		return vSpace + float3( 1.0f, 0.95f, 0.86f ) * ( 3.0f * vSunDisc + vCorona );
	}

	float3 GlobeSky( float3 vSkyColor, float3 vWorldPos )
	{
		float vWeight = smoothstep( 0.2f, 0.35f, GlobeBlend() );
		if ( vWeight <= 0.0f )
			return vSkyColor;
		float3 vRay = normalize( vWorldPos - vCamPos );
		float vPixel = max( length( fwidth( vRay ) ) * 0.6f, 0.00001f );
		float3 vDir = normalize( GlobeToPlanet( vRay ) );
		float3 vSun = GlobeSunPlanet();
		float3 vOffset = vCamPos - GlobeCenter();
		float vR = GlobeRadius();
		float vAlong = dot( vOffset, vRay );
		float vMiss = length( vOffset - vRay * min( vAlong, 0.0f ) );
		float3 vColor = float3( 0.0015f, 0.003f, 0.008f );
		float vHalo = pow( saturate( 1.0f - ( vMiss - vR ) / ( vR * 0.05f ) ), 3.0f ) * step( vR, vMiss );
		vColor += GlobeSunAndMoon( vDir, GlobeSpace( vDir, vPixel ), vPixel, vSun ) * ( 1.0f - vHalo );

		float vForward = pow( saturate( dot( vDir, vSun ) ), 6.0f );
		vColor += ( float3( 0.02f, 0.1f, 0.28f ) * 0.6f + float3( 1.0f, 0.62f, 0.32f ) * vForward * 0.9f ) * vHalo;
		float vDisc = vAlong * vAlong - dot( vOffset, vOffset ) + vR * vR;
		if ( vDisc >= 0.0f && vAlong < 0.0f )
		{

			float3 vRadial = normalize( vOffset + vRay * ( -vAlong - sqrt( vDisc ) ) );
			float3 vPoint = normalize( GlobeToPlanet( vRadial ) );
			float vEdge = vPoint.z > 0.0f ? 0.972f : 0.935f;
			float vIce = smoothstep( vEdge - 0.01f, vEdge + 0.006f, abs( vPoint.z ) + 0.03f * ( GlobeFbm( vPoint * 9.0f ) - 0.5f ) );
			float3 vIceColor = float3( 0.13f, 0.155f, 0.19f ) * ( 0.8f + 0.4f * GlobeFbm( vPoint * 23.0f + 4.0f ) );
			float3 vSurface = lerp( float3( 0.004f, 0.03f, 0.07f ), vIceColor, vIce );
			vColor = vSurface * ( 0.35f + 0.65f * saturate( dot( vPoint, vSun ) ) );
		}
		return lerp( vSkyColor, vColor, vWeight );
	}
]]

Code
[[

	static const float GLOBE_PI        = 3.14159265f;
	static const float GLOBE_CAM_FLAT  = 900.0f;
	static const float GLOBE_CAM_CURVE = 1000.0f;
	static const float GLOBE_CAM_FULL  = 1800.0f;
	static const float GLOBE_EQUATOR   = 672.0f / 2048.0f;
	static const float GLOBE_MIN_BLEND = 0.02f;

	static const float GLOBE_GMT_OFFSET  = 2793.0f;
	static const float GLOBE_SOUTH_ROW   = 0.17f;
	static const float GLOBE_NORTH_ROW   = 0.93f;

	float GlobeRadiusFull() { return MAP_SIZE_X / ( 2.0f * GLOBE_PI ); }

	float GlobeBlend() { return smoothstep( GLOBE_CAM_CURVE, GLOBE_CAM_FULL, vCamPos.y ); }

	float GlobeOceanWeight() { return smoothstep( GLOBE_CAM_FLAT, GLOBE_CAM_CURVE, vCamPos.y ); }

	float GlobeRadius() { return GlobeRadiusFull() / max( GlobeBlend(), GLOBE_MIN_BLEND ); }

	float2 GlobeFocus()
	{
		float3 vDir = normalize( vCamLookAtDir );
		float vT = max( 0.0f, vCamPos.y - WATER_HEIGHT ) / max( 0.05f, -vDir.y );
		float2 vFocus = vCamPos.xz + vDir.xz * vT;
		vFocus.y = clamp( vFocus.y, 0.0f, MAP_SIZE_Y );
		return vFocus;
	}

	float GlobeLatitude( float vRow )
	{
		float vProjected = ( clamp( vRow, 0.0f, MAP_SIZE_Y ) - GLOBE_EQUATOR * MAP_SIZE_Y ) / GlobeRadiusFull();
		return 2.5f * atan( exp( 0.8f * vProjected ) ) - 0.625f * GLOBE_PI;
	}

	float GlobeGeo() { return smoothstep( 0.5f, 1.0f, GlobeBlend() ); }

	float GlobeFocusLatitude() { return GlobeLatitude( GlobeFocus().y ) * GlobeGeo(); }

	float3 GlobeNormal( float3 vFlatPos )
	{
		float vBlend = GlobeBlend();
		float vScale = max( vBlend, GLOBE_MIN_BLEND );
		float vGeo = GlobeGeo();
		float2 vFocus = GlobeFocus();
		float vN = GlobeRadiusFull();
		float vLon = ( vFlatPos.x - vFocus.x ) / vN;
		vLon -= floor( vLon / ( 2.0f * GLOBE_PI ) + 0.5f ) * 2.0f * GLOBE_PI;
		vLon *= vScale;
		float vLatFocus = GlobeFocusLatitude();
		float vDLat = lerp( ( vFlatPos.z - vFocus.y ) / vN, GlobeLatitude( vFlatPos.z ) - GlobeLatitude( vFocus.y ), vGeo ) * vScale;
		float vLat = vLatFocus + vDLat;
		float3 vP = float3( cos( vLat ) * sin( vLon ), sin( vLat ), cos( vLat ) * cos( vLon ) );
		float3 vUp = float3( 0.0f, sin( vLatFocus ), cos( vLatFocus ) );
		float3 vNorth = float3( 0.0f, cos( vLatFocus ), -sin( vLatFocus ) );
		return normalize( float3( vP.x, dot( vP, vUp ), dot( vP, vNorth ) ) );
	}

	float3 GlobeWarp( float3 vFlatPos )
	{
		float vBlend = GlobeBlend();
		if ( vBlend <= 0.0f )
			return vFlatPos;
		float2 vFocus = GlobeFocus();
		float3 vNormal = GlobeNormal( vFlatPos );
		float3 vOffset = ( vNormal - float3( 0.0f, 1.0f, 0.0f ) ) * GlobeRadius() + vNormal * ( vFlatPos.y - WATER_HEIGHT );
		float3 vCurvedPos = float3( vFocus.x, WATER_HEIGHT, vFocus.y ) + vOffset;

		return lerp( vFlatPos, vCurvedPos, saturate( vBlend / GLOBE_MIN_BLEND ) );
	}

	float3 GlobeCenter()
	{
		float2 vFocus = GlobeFocus();
		return float3( vFocus.x, WATER_HEIGHT - GlobeRadius(), vFocus.y );
	}

	float GlobeFacing( float3 vFlatPos )
	{
		if ( GlobeBlend() <= 0.0f )
			return 1.0f;
		return dot( GlobeNormal( vFlatPos ), normalize( vCamPos - GlobeWarp( vFlatPos ) ) );
	}

	float GlobeVisible( float3 vFlatPos )
	{
		if ( GlobeBlend() <= 0.0f )
			return 1.0f;
		float vRows = min( vFlatPos.z + 2.0f, MAP_SIZE_Y + 2.0f - vFlatPos.z );
		return min( vRows, GlobeFacing( vFlatPos ) );
	}

	void GlobeBasis( out float3 vEast, out float3 vUp, out float3 vNorth )
	{
		float vLon = ( GlobeFocus().x - GLOBE_GMT_OFFSET ) / GlobeRadiusFull();
		float vLat = GlobeFocusLatitude();
		vEast = float3( -sin( vLon ), cos( vLon ), 0.0f );
		vUp = float3( cos( vLat ) * cos( vLon ), cos( vLat ) * sin( vLon ), sin( vLat ) );
		vNorth = float3( -sin( vLat ) * cos( vLon ), -sin( vLat ) * sin( vLon ), cos( vLat ) );
	}

	float3 GlobeToPlanet( float3 vWorld )
	{
		float3 vEast, vUp, vNorth;
		GlobeBasis( vEast, vUp, vNorth );
		return vWorld.x * vEast + vWorld.y * vUp + vWorld.z * vNorth;
	}

	float3 GlobeFromPlanet( float3 vPlanet )
	{
		float3 vEast, vUp, vNorth;
		GlobeBasis( vEast, vUp, vNorth );
		return float3( dot( vPlanet, vEast ), dot( vPlanet, vUp ), dot( vPlanet, vNorth ) );
	}

	float3 GlobeSunPlanet()
	{
		float3 vAnti = DayNight_Hour_SunDir.yzw;
		vAnti = dot( vAnti, vAnti ) > 0.000001f ? normalize( vAnti ) : float3( 0.0f, 0.0f, -1.0f );
		float vLon = atan2( -vAnti.x, -vAnti.z ) - 2.0f * GLOBE_PI * DayNight_Hour_SunDir.x;
		float vA = min( abs( vAnti.y ), 0.6f );
		float vY = -sign( vAnti.y ) * ( vA * sqrt( 1.0f - vA * vA ) - vA * vA ) / ( 1.0f - 2.0f * vA * vA );
		float vRow = ( acos( clamp( -vY, -1.0f, 1.0f ) ) / GLOBE_PI - GLOBE_SOUTH_ROW ) / ( GLOBE_NORTH_ROW - GLOBE_SOUTH_ROW ) * MAP_SIZE_Y;
		float vLat = GlobeLatitude( vRow );
		return float3( cos( vLat ) * cos( vLon ), cos( vLat ) * sin( vLon ), sin( vLat ) );
	}

	float3 GlobeOcean( float3 vFlatPos, float vShallow )
	{
		float3 vNormal = GlobeNormal( vFlatPos );
		float3 vToEye = normalize( vCamPos - GlobeWarp( vFlatPos ) );
		float vGeo = GlobeGeo();
		float3 vSun = normalize( lerp( normalize( vToEye + float3( -0.5f, 0.45f, -0.18f ) ), GlobeFromPlanet( GlobeSunPlanet() ), vGeo ) + float3( 0.0f, 0.0001f, 0.0f ) );
		float3 vColor = lerp( float3( 0.004f, 0.03f, 0.07f ), float3( 0.015f, 0.1f, 0.145f ), saturate( vShallow ) );
		float vLight = 0.6f + 0.4f * saturate( dot( vNormal, vSun ) );
		float vRim = pow( 1.0f - saturate( dot( vNormal, vToEye ) ), 4.0f );
		float vGlint = pow( saturate( dot( vNormal, normalize( vSun + vToEye ) ) ), 90.0f ) * vGeo;
		return vColor * vLight * ( 1.0f - 0.2f * vRim ) + float3( 0.017f, 0.07f, 0.19f ) * vRim * 0.6f
			+ float3( 1.0f, 0.92f, 0.78f ) * vGlint * 0.35f;
	}

]]

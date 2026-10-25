// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGBuildRules.h"

/** Pure selector rules: the component supplies the live pawn and encounter state. */
namespace RPGBuildSelectRules
{
	inline bool CanOpen(bool bBossDormant, bool bPlayerAlive, bool bGrounded, bool bInTransition)
	{
		return bBossDormant && bPlayerAlive && bGrounded && !bInTransition;
	}

	inline bool BuildForRow(int32 Row, ERPGBuild& OutBuild)
	{
		switch (Row)
		{
		case 0: OutBuild = ERPGBuild::Starter; return true;
		case 1: OutBuild = ERPGBuild::Strength; return true;
		case 2: OutBuild = ERPGBuild::Dex; return true;
		default: return false;
		}
	}

	inline bool ParseBuild(const FName BuildName, ERPGBuild& OutBuild)
	{
		return RPGBuildRules::Parse(BuildName.ToString(), OutBuild) == RPGBuildRules::EParse::Build;
	}

	inline FString RowText(int32 Row)
	{
		ERPGBuild Build = ERPGBuild::Starter;
		return BuildForRow(Row, Build)
			? RPGBuildRules::BuildLine(FName(RPGBuildRules::StyleOfBuild(Build)), RPGBuildRules::EDecision::Done)
			: FString();
	}
}

#include "C:\Program Files\Walabot\WalabotSDK\inc\WalabotAPI.h"
#include <iostream>
#include <stdio.h>
#include <string>

#ifdef __LINUX__
	#define CONFIG_FILE_PATH "/etc/walabotsdk.conf"
#else
	#define CONFIG_FILE_PATH "C:\\Program Files\\Walabot\\WalabotSDK\\bin\\.config"
#endif

#define CHECK_WALABOT_RESULT(result, func_name)					\
{																\
	if (result != WALABOT_SUCCESS)								\
	{															\
		const char* errorStr = Walabot_GetErrorString();		\
		std::cout << std::endl << func_name << " error: "       \
                  << errorStr << std::endl;                     \
		std::cout << "Press enter to continue ...";				\
		std::string dummy;										\
		std::getline(std::cin, dummy);							\
		return;													\
	}															\
}

void PrintImagingTargets(ImagingTarget*  targets, int numTargets)
{
	int targetIdx;

#ifdef __LINUX__
	printf("\033[2J\033[1;1H");
#else
	system("cls");
#endif

	if (numTargets > 0)
	{
		for (targetIdx = 0; targetIdx < numTargets; targetIdx++)
		{
			printf("Target #%d:\n\t\t type %s,\n\t\t angleDeg = %lf,\n\t\t xPosCm = %lf,\n\t\t yPosCm = %lf,\n\t\t zPosCm = %lf,\n\t\t wPosCm = %lf,\n\t\t amplitude = %lf\n ",
				targetIdx,
				targets[targetIdx].type == TARGET_TYPE_PIPE ? "Pipe" : "Unknown",
				targets[targetIdx].angleDeg,
				targets[targetIdx].xPosCm,
				targets[targetIdx].yPosCm,
				targets[targetIdx].zPosCm,
				targets[targetIdx].widthCm,
				targets[targetIdx].amplitude);
		}
	}
	else
	{
		printf("No targets detected\n");
	}
}

void Inwall_SampleCode()
{
	// --------------------
	// Variable definitions
	// --------------------
	WALABOT_RESULT res;

	// Walabot_GetStatus - output parameters
	APP_STATUS appStatus;
	double calibrationProcess; // Percentage of calibration completed, if status is STATUS_CALIBRATING

	// Walabot_GetImagingTargets - output parameters
	ImagingTarget* targets;
	int numTargets;

	// Walabot_GetRawImageSlice - output parameters
	int*	rasterImage;
	int		sizeX;
	int		sizeY;
	double	sliceDepth;
	double	power;

	// ------------------------
	// Initialize configuration
	// ------------------------
	double zArenaMin = 3;
	double zArenaMax = 8;
	double zArenaRes = 0.5;

	double xArenaMin = -3;
	double xArenaMax = 4;
	double xArenaRes = 0.5;

	double yArenaMin = -6;
	double yArenaMax = 4;
	double yArenaRes = 0.5;

	// ----------------------
	// Sample Code Start Here
	// ----------------------

	/*
	For an image to be received by the application, the following need to happen :
		1) Connect
		2) Configure
		3) Calibrate
		4) Start
		5) Trigger
		6) Get action
		7) Stop/Disconnect
	*/

	res = Walabot_Initialize(CONFIG_FILE_PATH);
	CHECK_WALABOT_RESULT(res, "Walabot_Initialize");

	//	1) Connect : Establish communication with Walabot.
	//	==================================================
	res = Walabot_ConnectAny();
	CHECK_WALABOT_RESULT(res, "Walabot_ConnectAny");

	//  2) Configure : Set scan profile and arena
	//	=========================================

	// Set Profile - short range . 
	//			Walabot recording mode is configured with the following attributes:
	//			-> Distance scanning through air; 
	//			-> lower - resolution images for a fast capture rate (useful for tracking quick movement)
	res = Walabot_SetProfile(PROF_SHORT_RANGE_IMAGING);
	CHECK_WALABOT_RESULT(res, "Walabot_SetProfile");

	// Set arena by Cartesian coordinates, with arena resolution :
	res = Walabot_SetArenaX(xArenaMin, xArenaMax, xArenaRes);
	CHECK_WALABOT_RESULT(res, "Walabot_SetArenaX");

	res = Walabot_SetArenaY(yArenaMin, yArenaMax, yArenaRes);
	CHECK_WALABOT_RESULT(res, "Walabot_SetArenaY");

	res = Walabot_SetArenaZ(zArenaMin, zArenaMax, zArenaRes);
	CHECK_WALABOT_RESULT(res, "Walabot_SetArenaZ");

	// Walabot filtering disable 
	res = Walabot_SetDynamicImageFilter(FILTER_TYPE_NONE);
	CHECK_WALABOT_RESULT(res, "Walabot_SetDynamicImageFilter");

	//	3) Start: Start the system in preparation for scanning.
	//	=======================================================
	res = Walabot_Start();
	CHECK_WALABOT_RESULT(res, "Walabot_Start");

	// 	4) Start Calibration 
	//  ====================
	res = Walabot_StartCalibration();
	CHECK_WALABOT_RESULT(res, "Walabot_StartCalibration");
	

	bool recording = true;

	while (recording)
	{
		// calibrates scanning to ignore or reduce the signals
		res = Walabot_GetStatus(&appStatus, &calibrationProcess);
		CHECK_WALABOT_RESULT(res, "Walabot_GetStatus");
		if (appStatus == STATUS_CALIBRATING || appStatus == STATUS_CALIBRATING_NO_MOVEMENT)
		{
			std::cout << "Calibrating: " << calibrationProcess << std::endl;
		}
		//	5) Trigger: Scan(sense) according to profile and record signals to be 
		//	available for processing and retrieval.
		//	====================================================================
		res = Walabot_Trigger();
		CHECK_WALABOT_RESULT(res, "Walabot_Trigger");

		//	6) 	Get action : retrieve the last completed triggered recording 
		//	================================================================
		res = Walabot_GetImagingTargets(&targets, &numTargets);
		CHECK_WALABOT_RESULT(res, "Walabot_GetImagingTargets");

		res = Walabot_GetRawImageSlice(&rasterImage, &sizeX, &sizeY, &sliceDepth, &power);
		CHECK_WALABOT_RESULT(res, "Walabot_GetRawImageSlice");

		if (appStatus == STATUS_SCANNING)
		{
			PrintImagingTargets(targets, numTargets);
		}
	}

	//	7) Stop and Disconnect.
	//	======================
	res = Walabot_Stop();
	CHECK_WALABOT_RESULT(res, "Walabot_Stop");

	res = Walabot_Disconnect();
	CHECK_WALABOT_RESULT(res, "Walabot_Disconnect");

	res = Walabot_Clean();
	CHECK_WALABOT_RESULT(res, "Walabot_Clean");
}

int main()
{
	Inwall_SampleCode();
}
